import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ingestion import KnowledgeBase

load_dotenv()

class TestGenAgent:
    def __init__(self):
        # Check for API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env")

        # Init Llama 3 with low temp for deterministic results
        self.llm = ChatGroq(
            temperature=0, 
            model_name="llama-3.3-70b-versatile",
            api_key=api_key
        )
        self.kb = KnowledgeBase()

    def generate_tests(self, user_query: str):
        try:
            # Fetch relevant docs from vector DB
            retriever = self.kb.get_retriever()
            docs = retriever.invoke(user_query)
            
            context_text = "\n\n".join([d.page_content for d in docs])

            if not context_text:
                return {"error": "No docs found. Please upload documents first."}

            # Strict JSON prompt to prevent hallucinations
            prompt = ChatPromptTemplate.from_template("""
            You are an expert QA Automation Lead. Generate test cases based STRICTLY on the provided context.
            
            RULES:
            1. Use ONLY the provided context.
            2. Output must be a JSON list of objects.
            3. Required fields: Test_ID, Feature, Test_Scenario, Expected_Result, Grounded_In.
            4. Return raw JSON only. No markdown.
            
            CONTEXT:
            {context}
            
            USER REQUEST:
            {query}
            
            OUTPUT JSON:
            """)

            # Run chain -> Get string output
            chain = prompt | self.llm | StrOutputParser()

            raw_response = chain.invoke({
                "context": context_text,
                "query": user_query
            })

            # Clean up markdown if LLM adds it
            clean_json = raw_response.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()

            # Parse and return dict
            return json.loads(clean_json)

        except Exception as e:
            print(f"ERROR in generate_tests: {str(e)}")
            return {"error": "Internal Server Error", "details": str(e)}