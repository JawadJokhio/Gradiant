import json
import re
from app.repositories.data_repository import DataRepository

class HistoryContextService:
    def __init__(self, data_repository: DataRepository):
        self.data_repository = data_repository

    def get_subject_context(self, query: str) -> str:
        """Focused RAG logic for Cambridge History (Syllabus 2059/01)"""
        context = ""
        query_lower = query.lower()
        data = self.data_repository.get_history_data()
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
