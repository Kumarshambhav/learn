from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS middleware for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class TopicRequest(BaseModel):
    topic: str

# Load OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(api_key=openai_api_key, temperature=0.7)

# Define prompt template
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

# Route for topic understanding
@app.post("/api/topic")
async def generate_topic_content(req: TopicRequest):
    try:
        # Create the runnable chain
        chain = prompt_template | llm

        # Get result using invoke()
        response = chain.invoke({"topic": req.topic})

        # Parse response into sections
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

    except Exception as e:
        return {
            "History": "Could not generate content.",
            "Why & How": "Could not generate content.",
            "Layman Explanation": "Could not generate content.",
            "Beginner Q&A": "Could not generate content.",
            "error": str(e)
        }


