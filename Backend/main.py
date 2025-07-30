# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os, re
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

app = FastAPI()

# CORS for frontend on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm1 = HuggingFaceEndpoint(
    repo_id="google/gemma-2-2b-it",
    task="text-generation"
)
llm = ChatHuggingFace(llm=llm1)

class TopicRequest(BaseModel):
    topic: str

@app.post("/api/topic")
async def generate_content(req: TopicRequest):
    try:
        prompt_template = PromptTemplate.from_template("""
You are an educational AI that explains topics to beginners.

Given the topic: "{topic}", generate:

1. History of the topic (150 words)
2. Why & How it works (150 words)
3. Explain in Layman Language (100 words)
4. 5 Beginner Q&A related to it

Output format must be:
{{
  "History": "...",
  "Why & How": "...",
  "Layman Explanation": "...",
  "Beginner Q&A": "..."
}}
""")
        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = chain.run(topic=req.topic)

        # Try to parse response using regex fallback
        sections = ["History", "Why & How", "Layman Explanation", "Beginner Q&A"]
        result = {}
        for section in sections:
            pattern = rf'"{section}"\s*:\s*"(.+?)"(?:,|\n|$)'
            match = re.search(pattern, response, re.DOTALL)
            if match:
                result[section] = match.group(1).strip()
            else:
                result[section] = "Could not parse this section."

        return result

    except Exception as e:
        print("Error:", str(e))
        return {
            "History": "Could not generate content.",
            "Why & How": "Could not generate content.",
            "Layman Explanation": "Could not generate content.",
            "Beginner Q&A": "Could not generate content.",
            "error": str(e)
        }
