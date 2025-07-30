from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os, re
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

app = FastAPI()

# ✅ CORS for local and deployed frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://learn-six-weld.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load HuggingFace LLM (replace with your working repo_id and key)
llm1 = HuggingFaceEndpoint(
    repo_id="nvidia/Llama-3_3-Nemotron-Super-49B-v1_5",
    task="text-generation"
)
llm = ChatHuggingFace(llm=llm1)

# ✅ Request model
class TopicRequest(BaseModel):
    topic: str

# ✅ Home route
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

# ✅ Favicon route
@app.get("/favicon.ico")
def favicon():
    return FileResponse("static/favicon.ico")

# ✅ Main route to generate content
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

        # ✅ New LangChain chain syntax
        chain = prompt_template | llm
        response = chain.invoke({"topic": req.topic})

        print("Raw LLM Response:", response)

        # ✅ Handle output format (response could be string or dict depending on model)
        raw_text = response if isinstance(response, str) else str(response)

        # ✅ Parse the response using regex
        sections = ["History", "Why & How", "Layman Explanation", "Beginner Q&A"]
        result = {}
        for section in sections:
            pattern = rf'"{section}"\s*:\s*"(.+?)"(?:,|\n|$)'
            match = re.search(pattern, raw_text, re.DOTALL)
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

