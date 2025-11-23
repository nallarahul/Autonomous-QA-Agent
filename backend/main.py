from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

# importing our own modules to handle the heavy lifting
from ingestion import KnowledgeBase
from rag_agent import TestGenAgent
from selenium_agent import SeleniumAgent

app = FastAPI(title="QA Agent Backend")

# spin up the knowledge base handler immediately
kb = KnowledgeBase()

# try to initialize the RAG agent
# wrapping this in a try-except block so the server doesn't crash if the API key is missing
try:
    test_gen_agent = TestGenAgent()
except Exception as e:
    print(f"Warning: TestGenAgent failed to start. Check your API keys. Error: {e}")
    test_gen_agent = None

# same thing for the selenium agent - we want the server to run even if this fails initially
try:
    selenium_agent = SeleniumAgent()
except Exception as e:
    print(f"Warning: SeleniumAgent failed to start. Error: {e}")
    selenium_agent = None


# defining the data structures we expect from the frontend
class TestRequest(BaseModel):
    query: str

class ScriptRequest(BaseModel):
    test_case: dict
    html_content: str

@app.get("/")
def home():
    # just a quick health check to see if the server is up
    return {"message": "QA Agent Backend is Running"}

@app.post("/upload-docs")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Takes the uploaded files and passes them to the ingestion engine
    to be chunked and stored in the vector database.
    """
    try:
        status = kb.ingest_documents(files)
        return {"status": "success", "message": status}
    except Exception as e:
        # if something breaks during file parsing, let the frontend know
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-tests")
async def generate_test_cases(request: TestRequest):
    """
    The brain of the operation. Takes the user's prompt, looks up context,
    and asks the LLM to plan out test cases.
    """
    # safety check to prevent 500 errors if the agent failed to load on startup
    if not test_gen_agent:
        raise HTTPException(status_code=500, detail="Test Agent is offline. Check server logs.")
        
    response = test_gen_agent.generate_tests(request.query)
    return response

@app.post("/generate-script")
async def generate_selenium_script(request: ScriptRequest):
    """
    Takes a specific test case and the raw HTML, then generates 
    the actual Selenium Python code to automate it.
    """
    if not selenium_agent:
        raise HTTPException(status_code=500, detail="Selenium Agent is offline. Check server logs.")
        
    response = selenium_agent.generate_script(request.test_case, request.html_content)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)