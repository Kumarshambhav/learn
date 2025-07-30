from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_community.llms import HuggingFaceHub
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class TopicRequest(BaseModel):
    topic: str

# Hugging Face setup
hf_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")

llm = HuggingFaceHub(
    repo_id="Qwen/Qwen3-Coder-480B-A35B-Instruct",  # or use any other supported HF model

    huggingfacehub_api_token=hf_api_key
)

# Prompt template
prompt_template = PromptTemplate(
    input_variables=["topic"],
    template="""
Explain the topic "{topic}" in the following structure:

### History
### Why & How
### Layman Explanation
### Beginner Q&A
"""
)

# Shared function to handle both POST and GET
async def handle_topic_request(topic: str):
    chain = prompt_template | llm
    response = chain.invoke({"topic": topic})

    result = {
        "History": "Could not generate content.",
        "Why & How": "Could not generate content.",
        "Layman Explanation": "Could not generate content.",
        "Beginner Q&A": "Could not generate content.",
    }

    if isinstance(response, str):
        parts = response.split("###")
        for part in parts:
            if "History" in part:
                result["History"] = part.replace("History", "").strip()
            elif "Why & How" in part:
                result["Why & How"] = part.replace("Why & How", "").strip()
            elif "Layman Explanation" in part:
                result["Layman Explanation"] = part.replace("Layman Explanation", "").strip()
            elif "Beginner Q&A" in part:
                result["Beginner Q&A"] = part.replace("Beginner Q&A", "").strip()

    return result

# POST endpoint
@app.post("/api/topic")
async def post_topic(req: TopicRequest):
    try:
        return await handle_topic_request(req.topic)
    except Exception as e:
        return {"error": str(e)}

# ✅ Added GET support for browser testing
@app.get("/api/topic")
async def get_topic(topic: str = Query(...)):
    try:
        return await handle_topic_request(topic)
    except Exception as e:
        return {"error": str(e)}


