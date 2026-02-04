from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
from huggingface_hub import InferenceClient
import re

# Load environment variables
load_dotenv()

app = FastAPI(title="Pakistan Geography Tutor API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Knowledge Datasets
BASE_DIR = os.path.dirname(__file__)
GEOG_DATA_PATH = os.path.join(BASE_DIR, "..", "data", "geography_data.json")
HIST_DATA_PATH = os.path.join(BASE_DIR, "..", "data", "history_data.json")

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

geography_data = load_json(GEOG_DATA_PATH)
history_data = load_json(HIST_DATA_PATH)

def get_subject_context(query, subject):
    """Enhanced RAG logic with past papers marking schemes"""
    context = ""
    query_lower = query.lower()
    
    if subject.lower() == "history":
        data = history_data
        matches = []
        marking_examples = []
        
        # [NEW] Check specific textbook topics first (Nigel Kelly context)
        topic_lower = query_lower.lower()
        specific_topics = data.get("specific_topics", {})
        
        # Generic Topic Search in specific_topics
        # This iterates over ALL topics in history_data, allowing access to the 30+ new topics
        found_specific = False
        topic_lower_words = set(re.findall(r'\w+', topic_lower))
        
        for key, topic_data in specific_topics.items():
            # Create keywords from key (e.g. "decline_of_mughal_rule" -> {"decline", "mughal", "rule"})
            key_words = set(key.split('_'))
            
            # Check overlap - simple heuristic: if significant overlap of meaningful words
            # Filter out common stop words if needed, but for now strict overlap
            common = topic_lower_words.intersection(key_words)
            
            # Match if at least 2 common words (to avoid false positives on 'of', 'the')
            # OR if key has only 1 word and it matches
            match = False
            if len(key_words) == 1 and len(common) == 1:
                match = True
            elif len(common) >= 2:
                match = True
            elif "1857" in key and "1857" in topic_lower: # Special date exception
                match = True
                
            if match:
                found_specific = True
                context += f"\n### TEXTBOOK CONTEXT: {topic_data.get('title', key)} ({topic_data.get('source', 'Notes')})\n"
                
                # Handle 'factors' style (Manual Entry)
                if "factors" in topic_data:
                    for factor, points in topic_data["factors"].items():
                        context += f"**{factor}**:\n"
                        for p in points:
                            context += f"- {p}\n"
                
                # Handle 'qa_pairs' style (Extracted Notes)
                if "qa_pairs" in topic_data:
                    context += "\n**Relevant Past Questions & Answers:**\n"
                    # Add top 3-5 relevant QAs or just all if reasonable? 
                    # Let's add all, but truncate if context gets too huge (LLM context window is large enough usually)
                    for qa in topic_data["qa_pairs"]:
                        context += f"Q: {qa['question']}\nA: {qa['answer']}\n\n"
                
                # Handle 'raw_text' fallback
                if "raw_text" in topic_data and "qa_pairs" not in topic_data and "factors" not in topic_data:
                     context += f"{topic_data['raw_text'][:2000]}...\n" # Truncate to avoid overflow
                
                context += "\n"
        
        if not found_specific:
             # Fallback or generic encouragement if no specific topic found
             pass

        # Search curated sections
        for section in ["section_1", "section_2", "section_3"]:
            for item in data.get(section, []):
                topic = item.get("topic", "").lower()
                if topic in query_lower or any(kw in query_lower for kw in topic.split()):
                    matches.append(json.dumps(item, indent=2))
        
        # Search past papers for relevant marking schemes
        past_papers = data.get("past_papers", {})
        for year, seasons in past_papers.items():
            for season, papers in seasons.items():
                for paper, content in papers.items():
                    mark_schemes = content.get("mark_scheme", [])
                    for scheme in mark_schemes:
                        question = scheme.get("question", "")
                        points = scheme.get("points", [])
                        
                        # Check if any marking points are relevant to the query
                        relevant_points = []
                        for point in points:
                            point_lower = point.lower()
                            # Check for keyword matches
                            if any(word in point_lower for word in query_lower.split() if len(word) > 3):
                                relevant_points.append(point)
                        
                        if relevant_points and len(marking_examples) < 3:
                            marking_examples.append({
                                "year": year,
                                "season": season.replace("_", " ").title(),
                                "paper": paper.replace("_", " ").title(),
                                "question": question,
                                "points": relevant_points[:5]  # Limit to 5 points per example
                            })
        
        # Build context string
        if matches:
            context = "\n### RELEVANT O-LEVEL HISTORY CONTEXT:\n" + "\n---\n".join(matches[:2])
        
        if marking_examples:
            context += "\n\n### CAMBRIDGE EXAMINER MARKING SCHEMES (Past Papers):\n"
            for example in marking_examples:
                context += f"\n**{example['year']} {example['season']} - {example['paper']} - Question {example['question']}**\n"
                context += "Marking Points:\n"
                for point in example['points']:
                    context += f"  • {point}\n"
            context += "\nUSE THESE MARKING SCHEMES AS REFERENCE for structuring your answer.\n"
            
    elif subject.lower() == "geography":
        # Search Geography GIS data for textual context
        matches = []
        for cat in ["forests", "livestock", "industries", "energy_resources", "mountain_ranges"]:
            for item in geography_data.get(cat, []):
                name = item.get("name", "").lower()
                if name in query_lower:
                    matches.append(f"{item.get('name')}: {item.get('facts') or item.get('description')}")
        
        if matches:
            context = "\n### RELEVANT GEOGRAPHY GIS CONTEXT:\n" + "\n".join(matches[:3])
            
    return context


def validate_history_answer(answer: str, marks: int) -> bool:
    """
    Cambridge 2059 Structural Validator
    Returns True if answer follows mark scheme rules
    """
    
    answer_lower = answer.lower()
    
    # ---- 4 MARK VALIDATION ----
    if marks == 4:
        # Must have exactly 2 reasons
        if "reason 1" not in answer_lower:
            return False
        if "reason 2" not in answer_lower:
            return False
        # Must NOT have evaluation or comparison
        if "judgement" in answer_lower or "however" in answer_lower or "more important" in answer_lower:
            return False
        return True
    
    # ---- 14 MARK VALIDATION ----
    if marks == 14:
        required_sections = [
            "introduction",
            "agree",
            "disagree",
            "final judgement"
        ]
        
        for sec in required_sections:
            if sec not in answer_lower:
                return False
        
        # Require comparison language
        comparison_words = ["however", "more significant", "less important", "in contrast", "whereas"]
        if not any(word in answer_lower for word in comparison_words):
            return False
        
        return True
    
    # Other marks pass by default
    return True


# Initialize LLM clients
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
hf_client = InferenceClient(token=os.getenv("HF_API_KEY")) if os.getenv("HF_API_KEY") else None

@app.get("/")
async def root():
    return {"message": "Pakistan Geography Tutor API is running"}

class TextQuery(BaseModel):
    query: str
    subject: str
    mode: str

CAIE_EXAM_SYSTEM_PROMPT = """
You are a Cambridge Assessment International Education (CAIE) O-Level Examiner and Subject Expert.
Your purpose is to provide highly accurate, curriculum-aligned, and structured answers for O-Level students.

You MUST format your response into EXACTLY four sections using the following headers:
### [1] Marking Scheme Breakdown
(Detail how marks are awarded point-by-point based on command words like 'Explain', 'Describe', or 'State')

### [2] Perfect O-Level Script
(Provide a complete model answer that would earn full marks. Use technical language appropriate for the subject)

### [3] Common Pitfalls
(List common mistakes students make for this specific topic that lead to mark loss)

### [4] Tutor Wisdom
(Provide a brief tip or mnemonic to help the student remember or master this concept)

General Rules:
* Use technical terms (e.g., 'alluvial soil' for Geog, 'Doctrine of Lapse' for History, 'opportunity cost' for Economics).
* Be concise and professional.
* Align the depth of the answer with the provided marks.
"""
HISTORY_LEVEL_MARKING = {
    3: "Level 1: Simple factual statements, no explanation.",
    4: "Level 2: Descriptive answer with some explanation.",
    5: "Level 3: Explained answer showing cause and effect.",
    7: "Level 3: Well-explained answer with clear reasoning.",
    10: "Level 3: One-sided analysis with a supported judgement.",
    14: "Level 4: Balanced evaluation with sustained judgement."
}

async def get_llm_response(prompt: str, subject: str, marks: int = 4):
    # Retrieve relevant context from local datasets (RAG-lite)
    context_data = get_subject_context(prompt, subject)
    
    # Subject-specific examiner personality
    if subject.lower() == "history":
        level_expectation = HISTORY_LEVEL_MARKING.get(
            marks,
            "Follow appropriate Cambridge level-based marking."
        )

        subject_context = f"""
=============================
HISTORY SUBJECT ENGINE – CAMBRIDGE 2059 + NIGEL KELLY ENFORCEMENT
=============================

This override applies ONLY when subject = HISTORY.
Do NOT modify behaviour for Geography, GIS or other subjects.

------------------------------------------------------------
PRIMARY ROLE
------------------------------------------------------------

Act as a Cambridge 2059 Pakistan Studies Paper 1 examiner.

Answers MUST reflect:

• Official Cambridge Level Descriptors
• Nigel Kelly supporting knowledge
• Examiner analytical judgement
• Mark scheme aligned structure
• Pakistan Movement syllabus accuracy

------------------------------------------------------------
CAMBRIDGE 2059 LEVEL DESCRIPTOR ENFORCEMENT
------------------------------------------------------------

LEVEL 1 (1–3 Marks)
• Simple statements
• Limited factual accuracy
• Descriptive or generalised

LEVEL 2 (4–6 Marks)
• Identifies reasons or factors
• Limited explanation
• Basic historical knowledge

LEVEL 3 (7–9 Marks)
• Clear explanation of factors
• Supporting historical evidence present
• Some analytical linkage

LEVEL 4 (10–12 Marks)
• Balanced explanation
• Multiple supported arguments
• Clear analysis and linkage

LEVEL 5 (13–14 Marks)
• Sustained evaluation
• Multi-factor comparison
• Chronological progression
• Consistent analytical judgement
• Fully supported conclusion

LEVEL EXPECTATION FOR THIS QUESTION:
{level_expectation}

------------------------------------------------------------
COMMAND WORD ENFORCEMENT (2059 RULE)
------------------------------------------------------------

Explain:
• Requires cause-effect explanation
• Requires evidence supported reasoning

Why:
• Requires multiple causal factors
• Requires linkage between causes

How far / Was X the main reason:
• Requires balanced evaluation
• Requires sustained judgement

Describe:
• Requires accurate factual narration only
• No evaluation allowed

------------------------------------------------------------
CAMBRIDGE MARK DISTRIBUTION ENFORCEMENT
------------------------------------------------------------

3 MARK QUESTIONS:
• 2–3 explained factual points
• Must include historical reference

4 MARK QUESTIONS:
• EXACTLY TWO developed reasons
• Each reason MUST contain:
  - Named event or factor
  - Accurate date or context
  - Cause-effect explanation
• No judgement allowed
• Maximum two paragraphs

5 MARK QUESTIONS:
• Several explained factors
• Each factor requires supporting evidence

7 MARK QUESTIONS:
• Detailed explanation of multiple causes
• Clear analytical development
• Supporting factual evidence required

10 MARK QUESTIONS:
• Balanced explanation required
• Must show two perspectives
• Evidence must support both arguments

14 MARK QUESTIONS:
• Sustained evaluation
• Multi-factor comparison
• Chronological movement progression
• Fully supported final judgement

------------------------------------------------------------
4 MARK STRUCTURE RULE
------------------------------------------------------------

Format:

Reason 1:
POINT → EVIDENCE → EXPLANATION

Reason 2:
POINT → EVIDENCE → EXPLANATION

If answer includes:
• Evaluation
• Comparison
• More than two reasons

→ Regenerate answer

------------------------------------------------------------
2059 BALANCE CONTROL SYSTEM
------------------------------------------------------------

Applies to:
• Why questions
• How far questions
• Main reason questions

Rules:

✔ Named factor limited to MAX TWO paragraphs
✔ Minimum TWO additional causes required
✔ Alternative causes must be equally or more developed

Distribution:

Named Factor = 30–40%
Other Causes = 60–70%

------------------------------------------------------------
NIGEL KELLY EVIDENCE ENFORCEMENT
------------------------------------------------------------

Every paragraph MUST follow:

POINT → EVIDENCE → EXPLANATION → LINK

Evidence MUST include:

• Named event
• Accurate date or time period
• Constitutional / political development
• Direct link to Pakistan Movement

Generic claims are forbidden.

------------------------------------------------------------
PAKISTAN MOVEMENT CORE COMPARISON POOL
------------------------------------------------------------

AI MUST automatically consider:

• Simla Deputation 1906
• Muslim League Formation 1906
• Morley-Minto Reforms 1909
• Lucknow Pact 1916
• Khilafat Movement
• Nehru Report 1928
• Jinnah 14 Points 1929
• Round Table Conferences
• Government of India Act 1935
• 1937 Elections and Congress Rule
• Lahore Resolution 1940
• Cripps Mission
• Cabinet Mission
• 1947 Partition developments

------------------------------------------------------------
14 MARK STRUCTURE ENFORCEMENT
------------------------------------------------------------

INTRODUCTION:
• Define named factor
• State debate clearly

AGREE SECTION:
• Importance of named factor
• Maximum TWO paragraphs
• Must include Nigel Kelly evidence
• Must include analytical impact

DISAGREE SECTION:
• Minimum THREE alternative developments
• Must follow chronological order
• Each must include:
  - Named event
  - Accurate date
  - Political or constitutional impact
  - Link to Pakistan Movement progression

FINAL JUDGEMENT:
• Directly answer question
• Compare all major factors
• Justify relative importance
• Introduce NO new evidence

------------------------------------------------------------
2059 PHASE PROGRESSION RULE
------------------------------------------------------------

Answers MUST demonstrate development across phases:

EARLY SAFEGUARD PHASE:
1906 – 1919

INTERWAR CONSTITUTIONAL CONFLICT:
1919 – 1939

PARTITION DEMAND PHASE:
1940 – 1947

Top level answers MUST cover at least TWO phases.

------------------------------------------------------------
EVALUATION QUALITY ENFORCEMENT
------------------------------------------------------------

High level answers MUST:

✔ Compare relative importance
✔ Explain WHY factors differed in impact
✔ Demonstrate political progression
✔ Maintain analytical tone throughout

Narrative storytelling → NOT allowed

------------------------------------------------------------
ANTI-NARRATIVE FILTER
------------------------------------------------------------

Reject answers that:

• Retell events chronologically without analysis
• Provide description without explanation
• Contain generic importance statements
• Lack constitutional or political context

------------------------------------------------------------
MARK CEILING DETECTOR
------------------------------------------------------------

AI must self-check:

If answer lacks comparison → Maximum Level 3
If answer lacks judgement → Maximum Level 4
If answer lacks multi-phase analysis → Cannot reach Level 5

------------------------------------------------------------
CAMBRIDGE EXAMINER LANGUAGE ENFORCEMENT
------------------------------------------------------------

Use analytical terminology:

• This marked a constitutional turning point because...
• This widened Hindu-Muslim political divergence...
• This strengthened Muslim demands for safeguards...
• However, a more decisive transformation occurred when...

------------------------------------------------------------
ANTI-GENERIC VALIDATION CHECK
------------------------------------------------------------

Before final output confirm:

✔ Named factor limited to two paragraphs
✔ Minimum two alternative causes included
✔ Evidence in every paragraph
✔ Dates and political developments included
✔ Sustained judgement present

If ANY fail → Regenerate answer

------------------------------------------------------------
OUTPUT FORMAT (MANDATORY)
------------------------------------------------------------

### [1] Marking Scheme Breakdown
Explain which Cambridge LEVEL is achieved and why.

### [2] Perfect O-Level Script
Write the examiner-standard answer following the required structure for this mark allocation.

### [3] Common Pitfalls
Explain why students lose marks or remain stuck in lower levels.

### [4] Tutor Wisdom
Give one practical exam technique to reach the highest level.

=============================
END OF ENGINE
=============================
"""

    elif subject.lower() == "geography":
        subject_context = """
        You are an expert O-Level Geography Examiner (Syllabus 2059/02).
        Focus on the environment of Pakistan, resources, topography, and agriculture.
        Reference specific locations, coordinate logic, and GIS data where possible.
        Use the provided context to ensure factual accuracy.
        Organize response using ### [1] to ### [4].
        """
    else:
        subject_context = f"You are an expert O-Level Examiner for {subject.capitalize()}. Provide accurate, curriculum-aligned answers formatted with ### [1] to ### [4]."

    # Construct final combined system prompt
    final_system_prompt = f"{CAIE_EXAM_SYSTEM_PROMPT}\n{subject_context}\n{context_data}"
    
    # Add mark-specific structure templates for History
    if subject.lower() == "history":
        if marks == 4:
            prompt += """

STRICT STRUCTURE REQUIRED:

Reason 1:
POINT → EVIDENCE → EXPLANATION

Reason 2:
POINT → EVIDENCE → EXPLANATION

Do NOT add judgement or conclusion.
"""
        
        if marks == 14:
            prompt += """

STRICT STRUCTURE REQUIRED:

Introduction

Agree Section (max two paragraphs)

Disagree Section (minimum three chronological factors)

Final Judgement
"""
    
    # Try Groq first with validation and retry
    if groq_client:
        try:
            for attempt in range(3):  # Retry enforcement (max 3 attempts)
                
                completion = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": final_system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4,  # Lower temperature for more consistent structure
                    max_tokens=2000,
                )
                
                output = completion.choices[0].message.content
                
                # VALIDATE HISTORY STRUCTURE
                if subject.lower() == "history":
                    if validate_history_answer(output, marks):
                        return output
                    else:
                        # Add regeneration instruction for next attempt
                        prompt += "\n\nYour previous answer did NOT follow Cambridge structure. Regenerate strictly following mark rules with proper section headings."
                else:
                    return output
            
            # If all attempts failed validation, return last attempt anyway
            return output
            
        except Exception as e:
            print(f"Groq API error: {e}")
    
    # Fallback to Hugging Face
    if hf_client:
        try:
            response = ""
            for message in hf_client.chat_completion(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                messages=[
                    {"role": "system", "content": final_system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                stream=True,
            ):
                response += message.choices[0].delta.content or ""
            return response
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            
    return "I'm sorry, I'm having trouble connecting to my intelligence systems right now. Please try again later or check your API keys."

@app.post("/ask-ai")
async def ask_ai(
    query: Optional[str] = Form(None),
    subject: str = Form(...),
    mode: str = Form(...),
    marks: int = Form(4),
    image: Optional[UploadFile] = File(None)
):
    prompt_query = query if query else "Explain the primary requirements for achieving top grades in this subject."
    
    # Enhance prompt with mark requirements and subject context
    if subject.lower() == "history":
        full_prompt = (
            f"Provide a {marks}-mark O-Level History answer. "
            f"Ensure the response meets Cambridge level-based marking criteria. "
            f"Question: {prompt_query}"
        )
    else:
        full_prompt = f"Provide a {marks}-mark answer for the following O-Level {subject} query: {prompt_query}"

    
    answer = await get_llm_response(full_prompt, subject, marks)
    
    return {"status": "success", "answer": answer}

@app.post("/analyze-map")
async def analyze_map(
    query: str = Form(...),
    image: UploadFile = File(...)
):
    query_lower = query.lower()
    results = {
        "status": "success",
        "features": [],
        "legend": [],
        "explanation": ""
    }

    found_any = False

    # Check for rain systems
    is_monsoon_query = "monsoon" in query_lower
    is_western_query = "western disturbance" in query_lower or "winter rain" in query_lower
    is_convectional_query = "convectional" in query_lower
    is_generic_rain_query = ("rain" in query_lower or "rainfall" in query_lower) and not (is_monsoon_query or is_western_query or is_convectional_query)

    for rs in geography_data.get("rain_systems", []):
        match = False
        if is_monsoon_query and rs["id"] == "monsoon": match = True
        elif is_western_query and rs["id"] == "western_disturbances": match = True
        elif is_convectional_query and rs["id"] == "convectional_rain": match = True
        elif is_generic_rain_query: match = True
        elif rs["name"].lower() in query_lower: match = True

        if match:
            for region in rs["regions"]:
                results["features"].append({
                    "type": "region",
                    "label": f"{rs['name']} ({region.get('intensity', 'Variable')})",
                    "data": [region],
                    "color": rs["color"],
                    "icon": "cloud-rain",
                    "opacity": 0.4 if region.get("intensity") == "Heavy" else 0.25 if region.get("intensity") == "Moderate" else 0.15
                })
            
            if not any(l["label"] == rs["name"] for l in results["legend"]):
                results["legend"].append({"label": rs["name"], "color": rs["color"], "icon": "cloud-rain"})
            
            results["explanation"] += f"### {rs['name']}\n"
            facts = rs["facts"]
            if isinstance(facts, dict):
                for field, val in facts.items():
                    results["explanation"] += f"- **{field}**: {val}\n"
            results["explanation"] += "\n"
            found_any = True

    # Check for landforms
    landform_keywords = ["landform", "doab", "plain", "delta", "physical"]
    is_landform_query = any(kw in query_lower for kw in landform_keywords)
    for lf in geography_data.get("landforms", []):
        if lf["id"] in query_lower or lf["name"].lower() in query_lower or is_landform_query:
            results["features"].append({
                "type": "region",
                "label": lf["name"],
                "data": lf["regions"],
                "color": lf["color"],
                "icon": "layers"
            })
            if not any(l["label"] == lf["name"] for l in results["legend"]):
                results["legend"].append({"label": lf["name"], "color": lf["color"], "icon": "layers"})
            results["explanation"] += f"**{lf['name']}**: {lf['facts']}\n"
            found_any = True

    # Check for livestock
    for ls in geography_data.get("livestock", []):
        if ls["id"] in query_lower or ls["name"].lower() in query_lower or "livestock" in query_lower:
            results["features"].append({
                "type": "region",
                "label": ls["name"],
                "data": ls["regions"],
                "color": ls["color"],
                "icon": "cow"
            })
            if not any(l["label"] == ls["name"] for l in results["legend"]):
                results["legend"].append({"label": ls["name"], "color": ls["color"], "icon": "cow"})
            results["explanation"] += f"**{ls['name']}**: {ls['facts']}\n"
            found_any = True

    # Check for mining methods
    for mm in geography_data.get("mining_methods", []):
        if mm["id"] in query_lower or mm["name"].lower() in query_lower or "mining method" in query_lower:
            for loc in mm["locations"]:
                results["features"].append({
                    "type": "point",
                    "label": f"{mm['name']} - {loc['name']}",
                    "data": [loc["coordinate"]],
                    "color": "#94a3b8",
                    "icon": "pickaxe"
                })
            if not any(l["label"] == mm["name"] for l in results["legend"]):
                results["legend"].append({"label": mm["name"], "color": "#94a3b8", "icon": "pickaxe"})
            results["explanation"] += f"**{mm['name']}**: {mm['facts']}\n"
            found_any = True

    # Check for specific industries (Steel, Fertilizer, Cement)
    for ind in geography_data.get("industries", []):
        if ind["id"].replace("_", " ") in query_lower or ind["name"].lower() in query_lower or "industry" in query_lower:
            for loc in ind["locations"]:
                results["features"].append({
                    "type": "point",
                    "label": f"{ind['name']} - {loc['name']}",
                    "data": [loc["coordinate"]],
                    "color": "#f87171",
                    "icon": "factory"
                })
            if not any(l["label"] == ind["name"] for l in results["legend"]):
                results["legend"].append({"label": ind["name"], "color": "#f87171", "icon": "factory"})
            results["explanation"] += f"**{ind['name']}**: {ind['facts']}\n"
            found_any = True

    # Check for airports
    is_intl_airport = "international airport" in query_lower or "intl airport" in query_lower
    is_domestic_airport = "domestic airport" in query_lower or "local airport" in query_lower
    is_generic_airport = "airport" in query_lower and not (is_intl_airport or is_domestic_airport)

    for ap in geography_data.get("airports", []):
        match = False
        if is_intl_airport and ap["id"] == "intl_airports": match = True
        elif is_domestic_airport and ap["id"] == "domestic_airports": match = True
        elif is_generic_airport: match = True
        elif ap["name"].lower() in query_lower: match = True

        if match:
            for loc in ap["locations"]:
                results["features"].append({
                    "type": "point",
                    "label": loc["name"],
                    "data": [loc["coordinate"]],
                    "color": "#6366f1",
                    "icon": "plane"
                })
            if not any(l["label"] == ap["name"] for l in results["legend"]):
                results["legend"].append({"label": ap["name"], "color": "#6366f1", "icon": "plane"})
            results["explanation"] += f"**{ap['name']}**: {ap['facts']}\n"
            found_any = True

    # Check for population
    for pop in geography_data.get("population", []):
        if pop["id"] in query_lower or pop["name"].lower() in query_lower or "population" in query_lower or "density" in query_lower:
            results["features"].append({
                "type": "region",
                "label": pop["name"],
                "data": pop["regions"],
                "color": pop["color"],
                "icon": "users"
            })
            if not any(l["label"] == pop["name"] for l in results["legend"]):
                results["legend"].append({"label": pop["name"], "color": pop["color"], "icon": "users"})
            results["explanation"] += f"**{pop['name']}**: {pop['facts']}\n"
            found_any = True

    # Check for provinces
    for prov in geography_data.get("provinces", []):
        if prov["id"] in query_lower or prov["name"].lower() in query_lower or "province" in query_lower:
            results["features"].append({
                "type": "region",
                "label": prov["name"],
                "data": [{"name": prov["name"], "coordinates": prov["coordinates"], "description": prov["facts"]}],
                "color": prov["color"],
                "icon": "map-pin"
            })
            if not any(l["label"] == prov["name"] for l in results["legend"]):
                results["legend"].append({"label": prov["name"], "color": prov["color"], "icon": "map-pin"})
            results["explanation"] += f"**{prov['name']}**: {prov['facts']}\n"
            found_any = True

    # Check for forests
    for forest in geography_data.get("forests", []):
        if forest["id"].replace("_", " ") in query_lower or forest["name"].lower() in query_lower or "forest" in query_lower:
            results["features"].append({
                "type": "region",
                "label": forest["name"],
                "data": forest["regions"],
                "color": forest["color"],
                "icon": "tree"
            })
            if not any(l["label"] == forest["name"] for l in results["legend"]):
                results["legend"].append({"label": forest["name"], "color": forest["color"], "icon": "tree"})
            
            facts = forest.get("facts", {})
            results["explanation"] += f"### {forest['name']} (Ecological Zone)\n"
            if isinstance(facts, dict):
                for field, val in facts.items():
                    results["explanation"] += f"- **{field}**: {val}\n"
            else:
                results["explanation"] += f"- **Facts**: {facts}\n"
            results["explanation"] += "\n"
            found_any = True

    # Check for deserts
    for desert in geography_data.get("deserts", []):
        if desert["id"].replace("_", " ") in query_lower or desert["name"].lower() in query_lower or "desert" in query_lower:
            results["features"].append({
                "type": "region",
                "label": desert["name"],
                "data": [{"name": desert["name"], "coordinates": desert["coordinates"], "description": desert["facts"]}],
                "color": "#fcd34d",
                "icon": "sun"
            })
            if not any(l["label"] == "Desert" for l in results["legend"]):
                results["legend"].append({"label": "Desert", "color": "#fcd34d", "icon": "sun"})
            results["explanation"] += f"**{desert['name']}**: {desert['facts']}\n"
            found_any = True

    # Check for livestock
    for ls in geography_data.get("livestock", []):
        if ls["id"] in query_lower or ls["name"].lower() in query_lower or "livestock" in query_lower or "buffalo" in query_lower or "sheep" in query_lower or "goat" in query_lower:
            results["features"].append({
                "type": "region",
                "label": ls["name"],
                "data": ls["regions"],
                "color": ls.get("color", "#4b5563"),
                "icon": "dog" # Using dog as placeholder for animal/livestock if sheep/cow not in lucide
            })
            if not any(l["label"] == "Livestock" for l in results["legend"]):
                results["legend"].append({"label": "Livestock", "color": ls.get("color", "#4b5563"), "icon": "dog"})
            results["explanation"] += f"**{ls['name']}**: {ls['facts']}\n"
            found_any = True

    # Check for mountain passes
    passes = geography_data.get("mountain_passes", [])
    # Also check nested passes in mountain ranges
    for mr in geography_data.get("mountain_ranges", []):
        if "passes" in mr:
            for p in mr["passes"]:
                # Avoid duplicates
                if not any(existing_p["name"] == p["name"] for existing_p in passes):
                    passes.append(p)
    
    for p in passes:
        if "pass" in query_lower or p["name"].lower() in query_lower:
            results["features"].append({
                "type": "point",
                "label": p["name"],
                "data": [p["coordinate"]],
                "color": "#fb923c",
                "icon": "mountain"
            })
            if not any(l["label"] == "Mountain Pass" for l in results["legend"]):
                results["legend"].append({"label": "Mountain Pass", "color": "#fb923c", "icon": "mountain"})
            results["explanation"] += f"**{p['name']}**: {p['facts']}\n"
            found_any = True

    # Plateaus enrichment logic (already handled by generic category search usually, but let's be explicit if needed)
    for plat in geography_data.get("plateaus", []):
        if plat["id"] in query_lower or plat["name"].lower() in query_lower or "plateau" in query_lower:
            results["features"].append({
                "type": "region",
                "label": plat["name"],
                "data": [{"name": plat["name"], "coordinates": plat["coordinates"], "description": plat["facts"]}],
                "color": plat.get("color", "#fca5a5"),
                "icon": "terrain" # Generic terrain icon
            })
            if not any(l["label"] == "Plateau" for l in results["legend"]):
                results["legend"].append({"label": "Plateau", "color": plat.get("color", "#fca5a5"), "icon": "terrain"})
            results["explanation"] += f"**{plat['name']}**: {plat['facts']}\n"
            found_any = True

    # Check for fruits
    for fruit in geography_data.get("fruits", []):
        if fruit["id"] in query_lower or fruit["name"].lower() in query_lower or (fruit["id"] == "citrus" and "kinnow" in query_lower):
            results["features"].append({
                "type": "region",
                "label": fruit["name"],
                "data": fruit["regions"],
                "color": fruit["color"],
                "icon": "apple"
            })
            results["legend"].append({"label": f"{fruit['name']} Orchard", "color": fruit["color"], "icon": "apple"})
            
            facts = fruit.get("facts", {})
            results["explanation"] += f"### {fruit['name']} Horticulture\n"
            if isinstance(facts, dict):
                for field, val in facts.items():
                    results["explanation"] += f"- **{field}**: {val}\n"
            results["explanation"] += f"- **Source**: {fruit.get('source', 'Agricultural Records')}\n\n"
            found_any = True

    # Check for crops
    for crop in geography_data.get("crops", []):
        if crop["id"] in query_lower or crop["name"].lower() in query_lower or (crop["id"] == "maize" and "corn" in query_lower):
            results["features"].append({
                "type": "region",
                "label": crop["name"],
                "data": crop["regions"],
                "color": crop["color"],
                "icon": "leaf"
            })
            results["legend"].append({"label": f"{crop['name']} Area", "color": crop["color"], "icon": "leaf"})
            
            facts = crop["facts"]
            results["explanation"] += f"### {crop['name']} Analysis (Major Crop)\n"
            if isinstance(facts, dict):
                for field, val in facts.items():
                    results["explanation"] += f"- **{field}**: {val}\n"
            results["explanation"] += f"- **Source**: {crop.get('source', 'Agricultural Census')}\n\n"
            found_any = True

    # Check for minerals
    for mineral in geography_data.get("minerals", []):
        if mineral["id"] in query_lower or mineral["name"].lower() in query_lower:
            for loc in mineral["locations"]:
                results["features"].append({
                    "type": "point",
                    "label": f"{mineral['name']} - {loc['name']}",
                    "data": [loc["coordinate"]],
                    "color": mineral["color"],
                    "icon": "pickaxe"
                })
            
            if not any(l["label"] == mineral["name"] for l in results["legend"]):
                results["legend"].append({"label": mineral["name"], "color": mineral["color"], "icon": "pickaxe"})
            
            results["explanation"] += f"### {mineral['name']} Analysis\n"
            results["explanation"] += f"- **Uses**: {mineral['uses']}\n"
            results["explanation"] += f"- **Significance**: {mineral['significance']}\n"
            results["explanation"] += f"- **Key Locations**: " + ", ".join([l['name'] for l in mineral['locations']]) + "\n\n"
            found_any = True

    # Check for specific mines
    for mine in geography_data.get("mines", []):
        if "mine" in query_lower or "salt" in query_lower or "emerald" in query_lower or "gem" in query_lower or mine["name"].lower() in query_lower:
            results["features"].append({
                "type": "point",
                "label": mine["name"],
                "data": [mine["coordinate"]],
                "color": "#94a3b8",
                "icon": "pickaxe"
            })
            if not any(l["label"] == "Mines" for l in results["legend"]):
                results["legend"].append({"label": "Mines", "color": "#94a3b8", "icon": "pickaxe"})
            results["explanation"] += f"**{mine['name']}**: {mine['facts']}\n"
            found_any = True

    # Check for energy resources
    for er in geography_data.get("energy_resources", []):
        match = er["type"].lower() in query_lower or er["name"].lower() in query_lower or "energy" in query_lower or "power" in query_lower
        if "hep" in query_lower and "hydroelectric" in er["type"].lower(): match = True
        
        if match:
            results["features"].append({
                "type": "point",
                "label": er["name"],
                "data": [er["coordinate"]],
                "color": "#facc15",
                "icon": "zap"
            })
            if not any(l["label"] == er["type"] for l in results["legend"]):
                results["legend"].append({"label": er["type"], "color": "#facc15", "icon": "zap"})
            results["explanation"] += f"**{er['name']}** ({er['type']}): {er['facts']}\n"
            found_any = True

    # Check for energy pipelines
    for ep in geography_data.get("energy_pipelines", []):
        if "pipeline" in query_lower or ep["name"].lower() in query_lower or "gas" in query_lower or "oil" in query_lower:
            results["features"].append({
                "type": "path",
                "label": ep["name"],
                "data": ep["path"],
                "color": ep["color"],
                "icon": "fuel"
            })
            if not any(l["label"] == "Pipelines" for l in results["legend"]):
                results["legend"].append({"label": "Pipelines", "color": ep["color"], "icon": "fuel"})
            results["explanation"] += f"**{ep['name']}**: {ep['facts']}\n"
            found_any = True

    # Check for transport
    transport_data = geography_data.get("transport", {})
    
    # Roads filtering
    is_motorway_query = "motorway" in query_lower
    is_highway_query = "highway" in query_lower or "gt road" in query_lower or "national highway" in query_lower
    is_generic_road = "road" in query_lower and not (is_motorway_query or is_highway_query)

    # Merge roads and trade_routes for simpler searching
    all_roads = transport_data.get("roads", []) + transport_data.get("trade_routes", [])

    for road in all_roads:
        match = False
        if is_motorway_query and road.get("id", "").startswith("m"): match = True
        elif is_highway_query and (road.get("id", "").startswith("n") or " (n-" in road["name"].lower() or "highway" in road["name"].lower() or "gt road" in road["name"].lower().replace("(gt)", "gt")): match = True
        elif is_generic_road: match = True
        elif road.get("id", "").lower() in query_lower or road["name"].lower() in query_lower: match = True

        if match:
            results["features"].append({
                "type": "path",
                "label": road["name"],
                "data": road["path"],
                "color": road.get("color", "#10b981"),
                "icon": "car"
            })
            if not any(l["label"] == "Motorways/Roads" for l in results["legend"]):
                results["legend"].append({"label": "Motorways/Roads", "color": road.get("color", "#10b981"), "icon": "car"})
            if road["name"] not in results["explanation"]:
                results["explanation"] += f"**{road['name']}**: {road['facts']}\n"
            found_any = True

    # Railways
    if "railway" in query_lower or "train" in query_lower or "track" in query_lower:
        for railway in transport_data.get("railways", []):
            results["features"].append({
                "type": "path",
                "label": railway["name"],
                "data": railway["path"],
                "color": railway["color"],
                "icon": "train"
            })
            if not any(l["label"] == "Railways" for l in results["legend"]):
                results["legend"].append({"label": "Railways", "color": railway["color"], "icon": "train"})
            results["explanation"] += f"**{railway['name']}**: {railway['facts']}\n"
            found_any = True

    for route in transport_data.get("trade_routes", []):
        if "cpec" in query_lower or route.get("id", "").lower() in query_lower or route["name"].lower() in query_lower:
            results["features"].append({
                "type": "path",
                "label": route["name"],
                "data": route["path"],
                "color": route.get("color", "#f97316"),
                "icon": "map"
            })
            if not any(l["label"] == "Trade Routes" for l in results["legend"]):
                results["legend"].append({"label": "Trade Routes", "color": route.get("color", "#f97316"), "icon": "map"})
            if route["name"] not in results["explanation"]:
                results["explanation"] += f"**{route['name']}**: {route['facts']}\n"
            found_any = True

    # Check for dams
    for dam in geography_data.get("dams", []):
        if "dam" in query_lower or dam["name"].lower() in query_lower or ("large dam" in query_lower and dam.get("type") == "large"):
            results["features"].append({
                "type": "point",
                "label": dam["name"],
                "data": [dam["coordinate"]],
                "color": "#22d3ee",
                "icon": "waves"
            })
            if not any(l["label"] == "Dams" for l in results["legend"]):
                results["legend"].append({"label": "Dams", "color": "#22d3ee", "icon": "waves"})
            results["explanation"] += f"**{dam['name']}** ({dam.get('type', 'dam').capitalize()}): {dam['facts']}\n"
            found_any = True

    # Check for ports (Improved specific filtering)
    is_dryport_query = "dryport" in query_lower or "dry port" in query_lower
    is_seaport_query = "seaport" in query_lower or "sea port" in query_lower or "deep sea port" in query_lower
    is_generic_port = "port" in query_lower and not (is_dryport_query or is_seaport_query)

    for port in geography_data.get("ports", []):
        match = False
        if is_dryport_query and port.get("type") == "dry": match = True
        elif is_seaport_query and port.get("type") == "sea": match = True
        elif is_generic_port: match = True
        elif port["name"].lower() in query_lower: match = True

        if match:
            results["features"].append({
                "type": "point",
                "label": port["name"],
                "data": [port["coordinate"]],
                "color": "#fbbf24",
                "icon": "anchor" if port.get("type") == "sea" else "ship"
            })
            label = f"{port.get('type', 'sea').capitalize()} Port"
            if not any(l["label"] == label for l in results["legend"]):
                results["legend"].append({"label": label, "color": "#fbbf24", "icon": "anchor" if port.get("type") == "sea" else "ship"})
            if port["name"] not in results["explanation"]:
                results["explanation"] += f"**{port['name']}** ({port.get('type', 'sea').capitalize()}): {port['facts']}\n"
            found_any = True

    # Check for fish farms
    for ff in geography_data.get("fish_farms", []):
        if "fish" in query_lower or ff["name"].lower() in query_lower:
            results["features"].append({
                "type": "region",
                "label": ff["name"],
                "data": ff["regions"],
                "color": ff["color"],
                "icon": "droplets"
            })
            results["legend"].append({"label": ff["name"], "color": ff["color"], "icon": "droplets"})
            results["explanation"] += f"**{ff['name']}**: {ff['facts']}\n"
            found_any = True

    # Check for drought areas
    for da in geography_data.get("drought_areas", []):
        if "drought" in query_lower or da["name"].lower() in query_lower:
            results["features"].append({
                "type": "region",
                "label": da["name"],
                "data": [{"name": da["name"], "coordinates": da["coordinates"], "description": da["facts"]}],
                "color": da["color"],
                "icon": "sun"
            })
            results["legend"].append({"label": "Drought Areas", "color": da["color"], "icon": "sun"})
            results["explanation"] += f"**{da['name']}**: {da['facts']}\n"
            found_any = True

    # Check for rivers
    for river in geography_data.get("rivers", []):
        if "river" in query_lower or river["id"] in query_lower or river["name"].lower() in query_lower:
            results["features"].append({
                "type": "path",
                "label": river["name"],
                "data": river["path"],
                "color": river.get("color", "#3b82f6"),
                "icon": "droplets"
            })
            if not any(l["label"] == river["name"] for l in results["legend"]):
                results["legend"].append({"label": river["name"], "color": river.get("color", "#3b82f6"), "icon": "droplets"})
            if river["name"] not in results["explanation"]:
                results["explanation"] += f"**{river['name']}**: {river['facts']}\n"
            found_any = True

    # Check for mountains and ranges
    for mountain in geography_data.get("mountains", []):
        if "mountain" in query_lower or mountain["id"] in query_lower or mountain["name"].lower() in query_lower:
            results["features"].append({
                "type": "point",
                "label": mountain["name"],
                "data": [mountain["coordinate"]],
                "color": "#9ca3af"
            })
            if not any(l["label"] == mountain["name"] for l in results["legend"]):
                results["legend"].append({"label": mountain["name"], "color": "#9ca3af", "icon": "mountain"})
            results["explanation"] += f"**{mountain['name']}**: {mountain['facts']} "
            found_any = True

    for m_range in geography_data.get("mountain_ranges", []):
        if "range" in query_lower or m_range["name"].lower() in query_lower or m_range["id"] in query_lower:
            results["features"].append({
                "type": "region",
                "label": m_range["name"],
                "data": [{"name": m_range["name"], "coordinates": m_range["coordinates"], "description": m_range["facts"]}],
                "color": "#94a3b8",
                "icon": "mountain"
            })
            peak = m_range["highest_peak"]
            results["features"].append({
                "type": "point",
                "label": f"Highest Peak: {peak['name']}",
                "data": [peak["coordinate"]],
                "color": "#ffffff",
                "icon": "mountain",
                "facts": f"{peak['name']} (Elevation: {peak['elevation']})"
            })
            found_any = True

    if not found_any:
        results["explanation"] = "I couldn't find specific geographic features for your query in our GIS database. However, I've analyzed the map context for you."

    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
