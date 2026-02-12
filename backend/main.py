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
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson import ObjectId
import pymongo

# Load environment variables
load_dotenv()

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-development-only-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
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
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

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
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
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

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

history_data = load_json(HIST_DATA_PATH)

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

def get_subject_context(query, subject="history"):
    """Focused RAG logic for Cambridge History"""
    context = ""
    query_lower = query.lower()
    
    data = history_data
    matches = []
    marking_examples = []
        
    # Check specific textbook topics first (Nigel Kelly context)
    specific_topics = data.get("specific_topics", {})
    found_specific = False
    topic_lower_words = set(re.findall(r'\w+', query_lower))
    
    for key, topic_data in specific_topics.items():
        key_words = set(key.split('_'))
        common = topic_lower_words.intersection(key_words)
        
        match = False
        if len(key_words) == 1 and len(common) == 1: match = True
        elif len(common) >= 2: match = True
        elif any(date in query_lower for date in re.findall(r'\d{4}', key)): match = True
            
        if match:
            found_specific = True
            context += f"\n### TEXTBOOK CONTEXT: {topic_data.get('title', key)} (Nigel Kelly Standards)\n"
            
            if "factors" in topic_data:
                for factor, points in topic_data["factors"].items():
                    context += f"**{factor}**:\n"
                    for p in points:
                        context += f"- {p}\n"
            
            if "qa_pairs" in topic_data:
                context += "\n**Relevant Past Questions & Answers (Examiner Style):**\n"
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
                    points = scheme.get("points", [])
                    
                    if any(word in question.lower() for word in query_lower.split() if len(word) > 4):
                        marking_examples.append({
                            "year": year,
                            "question": question,
                            "points": points[:5]
                        })
        
    if matches:
        context += "\n### O-LEVEL HISTORY ARCHIVE:\n" + "\n---\n".join(matches[:2])
    
    if marking_examples:
        context += "\n\n### CAMBRIDGE EXAMINER MARKING SCHEMES:\n"
        for example in marking_examples[:2]:
            context += f"\n**Question: {example['question']}**\n"
            for point in example['points']:
                context += f"  • {point}\n"
            
    return context

def validate_structure(answer: str, marks: int) -> bool:
    """Validates if the answer follow Cambridge structure rules"""
    a = answer.lower()
    if marks == 4:
        # Check for 2 PEEL paragraphs
        peels = re.findall(r'reason \d|point|evidence|explanation', a)
        return len(peels) >= 6
    if marks == 14:
        sections = ["introduction", "agree", "disagree", "judgement"]
        return all(s in a for s in sections)
    return True

async def get_llm_response(prompt: str, marks: int = 4, mode: str = "chat"):
    context = get_subject_context(prompt)
    
    # Implementing the 10-step Engine Logic in the System Prompt
    system_prompt = f"""
You are the Cambridge History Examiner Simulation Engine (Syllabus 2059/01).
Strictly follow the 10-step protocol:

STEP 1: Detect Command Word, Topic, and Personality.
STEP 2: Enforce Length: 4m(110-150w), 7m(220-260w), 14m(450-550w).
STEP 3: If personality mentioned, start with Full Name, DOB/DOD, and Historical Intro.
STEP 4: Structure:
- 4 Marks: Exactly 2 PEEL paragraphs.
- 7 Marks: 3 analytical PEEL paragraphs.
- 14 Marks: Full evaluation essay (Intro, Agree, Disagree, Final Judgement).
STEP 5: Use Nigel Kelly evidence (dates, names, acts) exclusively from context.
STEP 6: Always append [EXAMINER AUDIT] footer.
STEP 7: Analysis for Student Answers (Auto Mark mode).
STEP 8: Depth Analysis for 14 markers (progression & impact).
STEP 9: Output Discipline: Formal, clinical examiner tone.
STEP 10: Failsafe: Default to 4 marks if unspecified.

CONTEXT DATA FROM NIGEL KELLY / PAST PAPERS:
{context}

MARKING SCHEME RULES:
- 4 Marks: Reason 1 (P.E.E), Reason 2 (P.E.E). No evaluation.
- 7 Marks: 3 Reasons (P.E.E). Show cause-effect.
- 14 Marks: Balance 2 perspectives. Evaluation must have a clearly sustained conclusion.
"""

    try:
        if groq_client:
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
        
        # Fallback to HF
        if hf_client:
            res = hf_client.text_generation(
                f"<|system|>\n{system_prompt}\n<|user|>\nAnswer for {marks} marks: {prompt}\n<|assistant|>",
                model="Qwen/Qwen2.5-72B-Instruct",
                max_new_tokens=2000
            )
            return res
            
    except Exception as e:
        return f"Error: {str(e)}"
    
    return "Intelligence engines offline."

@app.post("/ask-ai")
async def ask_ai(
    query: Optional[str] = Form(None),
    subject: str = Form("history"),
    mode: str = Form("chat"),
    marks: int = Form(4),
    current_user: dict = Depends(get_current_user)
):
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    answer = await get_llm_response(query, marks, mode)
    
    # Save to history
    chat_entry = {
        "username": current_user["username"],
        "query": query,
        "answer": answer,
        "marks": marks,
        "mode": mode,
        "timestamp": datetime.utcnow()
    }
    await db.chats.insert_one(chat_entry)

    return {"answer": answer, "subject": "history", "marks": marks}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
