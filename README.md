# Autonomous QA Agent for Test Case and Script Generation

## 1\. Project Overview

This project involves the development of an intelligent, autonomous Quality Assurance (QA) agent. The system is designed to construct a "testing brain" by ingesting technical documentation (such as product specifications and UI/UX guidelines) and the HTML structure of a target web application.

Using Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs), the agent performs three critical functions:

1.  **Knowledge Ingestion:** Parses and vectorizes support documents to build a queryable knowledge base.
2.  **Test Case Generation:** Produces strictly documentation-grounded test plans, avoiding hallucinations.
3.  **Script Generation:** Converts generated test cases into fully executable Python Selenium scripts mapped to the actual HTML DOM elements.

## 2\. Technology Stack

  * **Programming Language:** Python 3.10+
  * **Backend Framework:** FastAPI
  * **Frontend Interface:** Streamlit
  * **LLM Provider:** Groq (Model: `llama-3.3-70b-versatile`)
  * **Orchestration Framework:** LangChain
  * **Vector Database:** ChromaDB
  * **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)
  * **Automation Library:** Selenium WebDriver

## 3\. Project Directory Structure

The repository is organized into distinct modules for backend logic, frontend presentation, and test assets.

```text
/automated-qa-agent
│
├── /backend                 # Core Application Logic
│   ├── main.py              # FastAPI application entry point
│   ├── ingestion.py         # Document parsing and vector database logic
│   ├── rag_agent.py         # RAG pipeline for test case generation
│   └── selenium_agent.py    # LLM pipeline for Selenium script generation
│
├── /frontend                # User Interface
│   └── ui.py                # Streamlit dashboard application
│
├── /assets                  # Support Documents and Target HTML
│   ├── checkout.html        # The target web page for testing
│   ├── product_specs.md     # Business logic and feature rules
│   └── ui_ux_guide.txt      # Visual and validation guidelines
│
├── .env                     # Environment variables (Excluded from version control)
├── .gitignore               # Git exclusion rules
├── init_db.py               # Utility script for manual database seeding
├── requirements.txt         # Python project dependencies
└── README.md                # Project documentation
```

## 4\. Prerequisites and Installation

### 4.1. Prerequisites

  * Python 3.10 or higher installed on your system.
  * A valid API Key from Groq.
  * Google Chrome installed (for Selenium testing).

### 4.2. Installation Steps

1.  **Clone the Repository**

    ```bash
    git clone <repository_url>
    cd automated-qa-agent
    ```

2.  **Create a Virtual Environment (Recommended)**

    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a file named `.env` in the root directory. Add your Groq API key:

    ```ini
    GROQ_API_KEY=gsk_your_actual_api_key_here
    ```

## 5\. How to Run the Application

The application requires two separate terminal processes running simultaneously: one for the backend API and one for the frontend UI.

### Step 1: Start the Backend Server

Open a terminal in the project root and execute:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

  * **Status Check:** The API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

### Step 2: Launch the Frontend Interface

Open a second terminal in the project root and execute:

```bash
streamlit run frontend/ui.py
```

  * The user interface will automatically open in your default browser at `http://localhost:8501`.

## 6\. Usage Guide

Follow this workflow to utilize the QA Agent:

### Phase 1: Knowledge Base Ingestion

1.  Navigate to the **Sidebar** in the Streamlit UI.
2.  Under **"1. Knowledge Base"**, upload the support documents (e.g., `product_specs.md`, `ui_ux_guide.txt`).
3.  Click the **"Ingest Documents"** button.
4.  Wait for the "System Online" confirmation. This indicates the documents have been parsed and stored in ChromaDB.

### Phase 2: Target Application Setup

1.  Under **"2. Target Application"** in the Sidebar, select your input method.
2.  Either paste the raw HTML code of `checkout.html` or upload the file directly.
3.  The system will confirm when the DOM structure is loaded.

### Phase 3: Test Case Generation

1.  Go to the **"Test Planner"** tab.
2.  In the chat interface, enter a prompt such as: *"Generate positive and negative test cases for the discount code feature."*
3.  The agent will retrieve rules from the uploaded documents and generate a structured list of test scenarios.

### Phase 4: Script Generation

1.  Switch to the **"Automation Studio"** tab.
2.  Select a specific test case from the generated list using the radio buttons.
3.  Click **"Generate Python Script"**.
4.  The system will analyze the HTML structure and the test case requirements to produce a Selenium script.
5.  Click **"Download .py File"** to save the script locally.

## 7\. Explanation of Included Support Documents

The `assets/` directory contains sample files used to demonstrate the system's capabilities:

1.  **checkout.html**:

      * **Description:** A single-page e-commerce checkout interface.
      * **Features:** Contains inputs for user details, radio buttons for shipping/payment, a discount code field, and dynamic total calculation logic. It serves as the DOM source for the Selenium agent.

2.  **product\_specs.md**:

      * **Description:** The functional requirements document.
      * **Usage:** The RAG agent uses this to understand business rules (e.g., "Discount code SAVE15 gives 15% off", "Express shipping costs $10"). Test cases are validated against these rules.

3.  **ui\_ux\_guide.txt**:

      * **Description:** The non-functional requirements document.
      * **Usage:** Provides validation rules for the UI (e.g., "Error messages must be red", "Pay Now button must be green").
