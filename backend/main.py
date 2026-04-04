from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn
import json
import os
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from dotenv import load_dotenv
from groq import Groq
from huggingface_hub import InferenceClient
import re
import motor.motor_asyncio
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson import ObjectId
import pymongo

# Load environment variables
load_dotenv()

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Use a default fallback ONLY for development; in production, this should fail.
    SECRET_KEY = "your-secret-key-for-development-only-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set")
db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=2000)
db = db_client.geography_tutor_db

app = FastAPI(title="Pakistan Geography Tutor - Personalized Examiner")

# Enable CORS for frontend
origins = ["*"] # Broaden for development, tighten later if needed

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTH UTILITIES ---
def verify_password(plain_password, hashed_password):
    try:
        # Standard bcrypt check - handles compatibility with passlib bcrypt hashes
        pwd_bytes = plain_password[:72].encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password):
    # Enforce 72-byte limit and return as string
    pwd_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            # Fallback for tokens missing 'sub' but having 'email' (from older Node.js sessions)
            username = payload.get("email")
            
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Try finding by username first, then by email (for Node.js compatibility)
    user = await db.users.find_one({"$or": [{"username": username}, {"email": username}]})
    if user is None:
        # Fallback for tokens signed externally (e.g., from Node.js)
        return {"username": username, "email": username, "status": "external_user"}
    return user

# --- SCHEMAS ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class LessonProgress(BaseModel):
    course: str
    progress: int
    weak_areas: List[str]
    last_active: datetime

# Load Knowledge Datasets
BASE_DIR = os.path.dirname(__file__)
HIST_DATA_PATH = os.path.join(BASE_DIR, "..", "data", "history_data.json")
GEOG_DATA_PATH = os.path.join(BASE_DIR, "..", "data", "geography_data.json")

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

history_data = load_json(HIST_DATA_PATH)
geography_data = load_json(GEOG_DATA_PATH)

# --- HELPER SCHEMAS ---
class WeaknessAnalysisResponse(BaseModel):
    weak_areas: List[str]
    improvement_plan: str
    summary: str

class PaperSession(BaseModel):
    session_name: str
    papers: List[str]

class YearlyPapers(BaseModel):
    year: str
    sessions: List[PaperSession]

# Initialize LLM clients
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
hf_client = InferenceClient(token=os.getenv("HF_API_KEY")) if os.getenv("HF_API_KEY") else None

# --- AUTH ENDPOINTS ---
@app.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    try:
        existing_user = await db.users.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or Email already registered")
        
        hashed_password = get_password_hash(user.password)
        new_user = {
            "username": user.username,
            "email": user.email,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/chat/history")
async def get_chat_history(current_user: dict = Depends(get_current_user)):
    history = await db.chats.find({"username": current_user["username"]}).sort("timestamp", -1).to_list(100)
    for h in history:
        h["_id"] = str(h["_id"])
    return history

def get_subject_context(query):
    """Focused RAG logic for Cambridge History (Syllabus 2059/01)"""
    context = ""
    query_lower = query.lower()
    data = history_data
    matches = []
    marking_examples = []
        
    # Check specific textbook topics first (Nigel Kelly context)
    specific_topics = data.get("specific_topics", {})
    topic_lower_words = set(re.findall(r'\w+', query_lower))
    
    
    for key, topic_data in specific_topics.items():
        key_words = set(key.split('_'))
        common = topic_lower_words.intersection(key_words)
        match = False
        if len(key_words) == 1 and len(common) == 1: match = True
        elif len(common) >= 2: match = True
        elif any(date in query_lower for date in re.findall(r'\d{4}', key)): match = True
            
        if match:
            context += f"\n### TEXTBOOK CONTEXT: {topic_data.get('title', key)} (Nigel Kelly Standards)\n"
            if "factors" in topic_data:
                for factor, points in topic_data["factors"].items():
                    context += f"**{factor}**:\n"
                    for p in points: context += f"- {p}\n"
            if "qa_pairs" in topic_data:
                context += "\n**Relevant Past Questions & Answers:**\n"
                for qa in topic_data["qa_pairs"][:3]:
                    context += f"Q: {qa['question']}\nA: {qa['answer']}\n\n"
            if "raw_text" in topic_data:
                 context += f"{topic_data['raw_text'][:1000]}...\n"
            context += "\n"
    
    # Search curated sections
    for section in ["section_1", "section_2", "section_3"]:
        for item in data.get(section, []):
            topic = item.get("topic", "").lower()
            if topic in query_lower or any(kw in query_lower for kw in topic.split() if len(kw) > 3):
                matches.append(json.dumps(item, indent=2))
        
    # Search past papers for relevant marking schemes
    past_papers = data.get("past_papers", {})
    for year, seasons in past_papers.items():
        for season, papers in seasons.items():
            for paper, content in papers.items():
                mark_schemes = content.get("mark_scheme", [])
                for scheme in mark_schemes:
                    question = scheme.get("question", "")
                    # Fix field mapping for points and retrieve examiner_tips
                    points = scheme.get("mark_scheme_points", scheme.get("points", []))
                    tips = scheme.get("examiner_tips", [])
                    
                    if any(word in question.lower() for word in query_lower.split() if len(word) > 4):
                        marking_examples.append({
                            "year": year, 
                            "question": question, 
                            "points": points[:5],
                            "tips": tips
                        })
        
    if matches:
        context += "\n### O-LEVEL HISTORY ARCHIVE:\n" + "\n---\n".join(matches[:2])
    
    if marking_examples:
        context += "\n\n### CAMBRIDGE EXAMINER MARKING SCHEMES & TIPS:\n"
        for example in marking_examples[:2]:
            context += f"\n**Question: {example['question']}**\n"
            for point in example['points']: context += f"  • {point}\n"
            if example['tips']:
                context += "  **Tutor Wisdom/Tips:**\n"
                for tip in example['tips']: context += f"  - {tip}\n"
            
    return context

async def get_llm_response(prompt: str, marks: int = 4, mode: str = "chat"):
    context = get_subject_context(prompt)
    system_prompt = f"""
You are the Cambridge History Examiner Simulation Engine (Syllabus 2059/01).

===== NON-NEGOTIABLE EXAMINER RULES =====

STEP 1 — QUESTION TYPE DETECTION
Detect:
• command word
• topic
• personality vs event

STEP 2 — PERSONALITY BIO RULE
If a named individual appears:
START answer with:
• Full name
• Birth–death years
• Role/title
• Movement association

STEP 3 — MARK STRUCTURE ENFORCEMENT

4 MARK:
• EXACTLY TWO reasons
• Each reason = POINT → EVIDENCE(date/event) → EXPLANATION
• NO evaluation
• NO comparison
• NO conclusion

7 MARK:
• THREE developed reasons
• No sustained judgement

14 MARK:
• INTRODUCTION
• AGREE (max 2 paragraphs)
• DISAGREE (≥3 developments chronological)
• FINAL JUDGEMENT
• Sustained comparison required

If violated → internally regenerate.

STEP 4 — NIGEL KELLY EVIDENCE CONTROL
Only use evidence from CONTEXT.
Every paragraph must include:
• named event
• date
• Pakistan Movement linkage (if relevant)
STEP 4.5 — TEMPORAL BOUNDARY ENFORCEMENT

If the question specifies a date range:

• ALL evidence MUST fall within that time period
• Events outside the range are STRICTLY FORBIDDEN
• No forward referencing beyond the end year
• No later outcomes used as evidence
• Argument must be built using developments ONLY within timeframe

If violation occurs → internally regenerate answer

TEMPORAL RELEVANCE RULE:

If evaluating significance within a period:

• Significance must be explained in relation to developments within same period
• Later consequences cannot be used as justification

STEP 5 — LENGTH NORMALISER
Target:
4m → ~120 words
7m → ~240 words
14m → ~500 words

Trim or extend silently.

STEP 6 — EXAMINER BAND GENERATOR

Use rubric:

4m:
2 reasons complete → 4
1 developed → 2–3
simple list → 1

7m:
3 developed → 6–7
2 developed → 4–5
descriptive → 2–3

14m:
evaluation + comparison → 12–14
some judgement → 8–11
narrative → 4–7

STEP 7 — EXAMINER AUDIT FORMAT
Append ONLY:

[EXAMINER AUDIT: X/{{marks}}]
Band Level: L?
Reason: concise examiner rationale

STEP 8 — TUTOR WISDOM
Always conclude with a concise, one-sentence "Tutor Wisdom" section.
FORMAT:
### [4] Tutor Wisdom
[Your dynamic advice here based on the examiner tips or question logic]

STEP 9 — TONE
Formal Cambridge examiner.

STEP 10 — FAILSAFE
If uncertain → default to 4m rules.

===== CONTEXT =====
{context}
"""
    # Try Groq first (Primary)
    if groq_client:
        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Answer for {marks} marks: {prompt}" if mode == "chat" else f"Grade this student answer for {marks} marks: {prompt}"}
                ],
                temperature=0.3,
                max_tokens=2500
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq Error: {str(e)}. Falling back to secondary engine...")

    # Fallback to Hugging Face (Secondary)
    if hf_client:
        try:
            return hf_client.text_generation(
                f"<|system|>\n{system_prompt}\n<|user|>\nAnswer for {marks} marks: {prompt}\n<|assistant|>",
                model="Qwen/Qwen2.5-72B-Instruct",
                max_new_tokens=2000
            )
        except Exception as e:
            return f"Error with all intelligence engines (HF): {str(e)}"
    
    # If no providers are available
    return "Intelligence engines offline: Please check your API keys in the .env file."
    
@app.post("/ask-ai")
async def ask_ai(
    query: str = Form(...),
    marks: int = Form(4),
    current_user: dict = Depends(get_current_user)
):
    answer = await get_llm_response(query, marks)
    
    # Save to history
    chat_entry = {
        "username": current_user["username"],
        "query": query,
        "answer": answer,
        "marks": marks,
        "mode": "chat",
        "timestamp": datetime.utcnow()
    }
    await db.chats.insert_one(chat_entry)

    return {"answer": answer, "marks": marks}

# --- NEW CAMBRIDGE ASSISTANT STYLE ENDPOINTS ---

@app.get("/papers/{subject}/years")
async def get_paper_years(subject: str):
    data = history_data if subject.lower() == "history" else geography_data
    past_papers = data.get("past_papers", {})
    return sorted(list(past_papers.keys()), reverse=True)

@app.get("/papers/{subject}/{year}")
async def get_paper_sessions(subject: str, year: str):
    data = history_data if subject.lower() == "history" else geography_data
    year_data = data.get("past_papers", {}).get(year, {})
    return list(year_data.keys())

@app.get("/papers/{subject}/{year}/{session}")
async def get_paper_content(subject: str, year: str, session: str):
    data = history_data if subject.lower() == "history" else geography_data
    session_data = data.get("past_papers", {}).get(year, {}).get(session, {})
    return session_data

@app.get("/analyze-weakness", response_model=WeaknessAnalysisResponse)
async def analyze_weakness(current_user: dict = Depends(get_current_user)):
    # Fetch user's recent chat history
    history = await db.chats.find({"username": current_user["username"]}).sort("timestamp", -1).to_list(10)
    
    if not history:
        return {
            "weak_areas": ["Not enough data yet"],
            "improvement_plan": "Start interacting with the AI examiners to see your progress!",
            "summary": "Begin your journey by asking questions or practicing paper solutions."
        }

    # Prepare historical context for LLM
    interactions = ""
    for h in history:
        interactions += f"Q: {h['query']}\nFeedback: {h['answer']}\n\n"

    analysis_prompt = f"""
    Analyze the following recent exam practice interactions for student "{current_user['username']}".
    Based on the examiner's feedback and the student's questions, identify:
    1. Three specific academic weak areas (be very specific like '1947 partition reasons' or 'topographic map symbols').
    2. A one-paragraph actionable improvement plan.
    3. A brief summary of overall performance.

    INTERACTIONS:
    {interactions}

    RETURN ONLY A JSON OBJECT with keys: "weak_areas" (list), "improvement_plan" (string), "summary" (string).
    """

    try:
        if groq_client:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            result = json.loads(completion.choices[0].message.content)
            return result
    except Exception as e:
        print(f"Weakness Analysis Error: {str(e)}")

    # Fallback/Dummy Analysis if LLM fails
    return {
        "weak_areas": ["Recent Topics Analysis"],
        "improvement_plan": "Focus on consistent practice with diverse question types.",
        "summary": "Keep practicing to generate more detailed insights."
    }

CATEGORY_ALIASES = {
    "provinces": ["province", "provinces", "administrative"],
    "crops": ["crop", "crops", "agriculture", "farming"],
    "livestock": ["livestock", "animals"],
    "fruits": ["fruit", "fruits"],
    "forests": ["forest", "forests", "vegetation"],
    "energy": ["energy", "power", "electricity"],
    "minerals": ["mineral", "minerals", "mining"],
    "rivers": ["river", "rivers"],
    "barrages": ["barrage", "barrages"],
    "ports": ["port", "seaport", "harbor"],
    "dryports": ["dryport", "dry port"],
    "airports": ["airport", "airports"],
    "dams": ["dam", "dams"],
    "industries": ["industry", "industries", "industrial"],
    "pipelines": ["pipeline", "pipelines"],
    "population": ["population", "density"],
    "landforms": ["landform", "relief", "plains"],
    "rain": ["rain", "monsoon", "climate"],
    "mountains": ["mountain", "range"],
    "deserts": ["desert"],
    "plateaus": ["plateau"],
    "passes": ["pass"],
    "glaciers": ["glacier"],
    "canals": ["canal"],
    "fish": ["fish", "fishing"],
    "drought": ["drought", "arid"],
    "industrial_zones": ["sez", "industrial zone"]
}

def detect_category(query):
    query = query.lower()
    
    for category, keywords in CATEGORY_ALIASES.items():
        for kw in keywords:
            if re.search(rf"\b{kw}\b", query):
                return category
    
    return None

def match_entities(data, query):
    query = query.lower()
    results = []

    for category, items in data.items():
        if isinstance(items, dict):
            items = [i for sub in items.values() for i in sub]

        for item in items:
            name = item.get("name", "").lower()
            item_id = item.get("id", "").lower()

            # Priority scoring
            score = 0

            if query == name:
                score = 100
            elif name in query:
                score = 80
            elif any(word in name for word in query.split()):
                score = 50

            if score > 0:
                results.append((score, category, item))

    return sorted(results, reverse=True)

def convert_to_feature(category, item):
    features = []

    if "path" in item:
        features.append({
            "type": "path",
            "label": item.get("name", ""),
            "data": item["path"],
            "color": item.get("color", "#3b82f6")
        })

    elif "locations" in item:
        for loc in item["locations"]:
            features.append({
                "type": "point",
                "label": loc.get("name", item.get("name", "")),
                "data": [loc["coordinate"]],
                "color": item.get("color", "#f43f5e"),
                "facts": loc.get("description", item.get("facts")),
                "icon": item.get("icon", "map-pin")
            })

    elif "coordinate" in item:
        features.append({
            "type": "point",
            "label": item.get("name", ""),
            "data": [item["coordinate"]],
            "color": item.get("color", "#f43f5e"),
            "facts": item.get("facts"),
            "icon": item.get("icon", "anchor" if "port" in category else "map-pin")
        })

    elif "regions" in item or "coordinates" in item:
        region_data = item.get("regions") or [{"name": item.get("name", ""), "coordinates": item["coordinates"], "description": item.get("facts")}]
        features.append({
            "type": "region",
            "label": item.get("name", ""),
            "data": region_data,
            "color": item.get("color", "#10b981" if "regions" in item else "#fbbf24")
        })

    return features

@app.post("/analyze-map")
async def analyze_map(
    query: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    query_lower = query.lower()
    
    category = detect_category(query_lower)
    entity_matches = match_entities(geography_data, query_lower)

    features = []
    matched_facts = []

    # CASE 1: Strong entity match
    if entity_matches:
        top_matches = entity_matches[:5]

        for _, cat, item in top_matches:
            matched_facts.append(f"{item.get('name')}: {item.get('facts', '')}")
            features.extend(convert_to_feature(cat, item))

    # CASE 2: Category-based retrieval
    elif category:
        items = geography_data.get(category, [])

        if isinstance(items, dict):
            items = [i for sub in items.values() for i in sub]

        for item in items[:10]:
            matched_facts.append(f"{item.get('name')}: {item.get('facts', '')}")
            features.extend(convert_to_feature(category, item))

    # CASE 3: fallback
    else:
        matched_facts.append("No strong geographical match found.")

    # 2. Generate LLM Explanation

    knowledge_context = "\n".join(matched_facts[:10]) # Limit context to avoid token bloat
    
    system_prompt = f"""
    You are the Cambridge Geography Examiner (Syllabus 2217/02).
    Provide an expert geographical breakdown for: "{query}" in the context of Pakistan.
    
    ===== GEOGRAPHICAL KNOWLEDGE BASE =====
    {knowledge_context}
    ========================================

    Format your response with:
    ### [1] Curriculum Context
    [Brief overview]
    
    ### [2] Distribution Analysis
    [Where these are found and WHY - physical factors like relief, soil, climate]
    
    ### [3] Economic Significance
    [Impact on Pakistan's GDP, trade, or local livelihoods]
    
    ### [4] Tutor Wisdom
    [One-sentence exam tip]
    
    Use technical terms (Relief, Alluvial, Rabi/Kharif, Perennial).
    Keep it concise (~300 words).
    """
    
    explanation = "Intelligence engines offline."
    if groq_client:
        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.3
            )
            explanation = completion.choices[0].message.content
        except Exception as e:
            print(f"Groq Error in GIS: {str(e)}")

    return {
        "features": features,
        "explanation": explanation,
        "query": query
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)