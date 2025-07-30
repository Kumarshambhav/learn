from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os, re
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

app = FastAPI()

# CORS config for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://learn-six-weld.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load HuggingFace LLM
llm1 = HuggingFaceEndpoint(
    repo_id="nvidia/Llama-3_3-Nemotron-Super-49B-v1_5",
    task="text-generation"
)
llm = ChatHuggingFace(llm=llm1)

# Request model
class TopicRequest(BaseModel):
    topic: str

# ✅ Root route to avoid 404 on "/"
@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <head><title>LaymanLearn Backend</title></head>
        <body style="font-family: sans-serif;">
            <h2>🚀 FastAPI backend is running!</h2>
            <p>POST to <code>/api/topic</code> with a JSON body like:</p>
            <pre>{ "topic": "Blockchain" }</pre>
        </body>
    </html>
    """

# ✅ Favicon handler (optional)
@app.get("/favicon.ico")
def favicon():
    return FileResponse("static/favicon.ico")  # Make sure this file exists if you use it

# ✅ Core API endpoint
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

        # Regex-based section extraction
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
