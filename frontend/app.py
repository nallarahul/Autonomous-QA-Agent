import streamlit as st
import requests

# Backend API URL
API_URL = "http://localhost:8000"

# --- Page Configuration ---
st.set_page_config(
    page_title="QA Automation Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for cleaner look ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        margin-bottom: 1rem;
    }
    /* Fix for chat input sticking to bottom */
    .stChatInput {
        position: fixed;
        bottom: 0;
        margin-bottom: 20px;
        border: 1.5px solid #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Autonomous QA Agent")
st.markdown("### AI-Powered Test Case & Script Generation")
st.markdown("---")

# --- Session State Initialization ---
if 'test_cases' not in st.session_state:
    st.session_state['test_cases'] = []
if 'generated_script' not in st.session_state:
    st.session_state['generated_script'] = ""
if 'kb_built' not in st.session_state:
    st.session_state['kb_built'] = False
# NEW: We need a message history to keep the chat above the input bar
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "assistant", "content": "👋 Hi! I'm your AI QA Lead. Build the Knowledge Base, then ask me to generate test cases."}
    ]

# --- SIDEBAR: Configuration Center ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Section 1: Knowledge Base
    st.subheader("1. Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload Requirements (MD, TXT, PDF)", 
        accept_multiple_files=True,
        type=["md", "txt", "json", "pdf"],
        help="Upload product specs or UI guides here."
    )
    
    if st.button("Build Knowledge Base", type="primary"):
        if uploaded_files:
            files = [("files", (f.name, f, "text/plain")) for f in uploaded_files]
            with st.spinner("Parsing & Vectorizing..."):
                try:
                    response = requests.post(f"{API_URL}/upload-docs", files=files)
                    if response.status_code == 200:
                        st.session_state['kb_built'] = True
                        st.success("Knowledge Base is ready !!")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Failed: {e}")
        else:
            st.warning("Upload files first.")
            
    # Status Indicator
    if st.session_state['kb_built']:
        st.markdown('<div class="success-box">AI Brain: <b>Active</b></div>', unsafe_allow_html=True)
    else:
        st.info("ℹ AI Brain: Empty")

    st.divider()
    
    # Section 2: Target Application
    st.subheader("2. Target Application")
    input_method = st.radio("Input Source:", ["Paste HTML Code", "Upload HTML File"])
    
    html_content = ""
    if input_method == "Paste HTML Code":
        html_content = st.text_area("Paste 'checkout.html':", height=200, placeholder="<html>...</html>")
    else:
        html_file = st.file_uploader("Upload HTML", type=["html"])
        if html_file:
            html_content = html_file.read().decode("utf-8")
            st.markdown('<div class="success-box">HTML file: <b>Loaded</b></div>', unsafe_allow_html=True)
    
    # Store HTML in session state so it persists between tabs
    if html_content:
        st.session_state['html_content'] = html_content

# --- MAIN AREA ---

tab1, tab2 = st.tabs(["Generate Test Cases", "Generate Code"])

# --- TAB 1: Intelligent Test Planning (Chat Interface) ---
with tab1:
    st.subheader("AI QA Lead")
    
    # 1. DISPLAY HISTORY FIRST (This ensures messages appear above input)
    for msg in st.session_state['messages']:
        with st.chat_message(msg["role"]):
            # If it's a list, it means these are test cases (JSON data)
            if isinstance(msg["content"], list):
                st.write(f"I found **{len(msg['content'])} test scenarios** based on your docs:")
                for tc in msg["content"]:
                    with st.expander(f"{tc.get('Test_ID', 'ID')}: {tc.get('Test_Scenario')}"):
                        st.markdown(f"**Expected Result:** {tc.get('Expected_Result')}")
                        st.markdown(f"**Source:** _{tc.get('Grounded_In')}_")
            else:
                # Normal text message
                st.write(msg["content"])

    # 2. INPUT BAR AT BOTTOM
    if user_query := st.chat_input("Ex: Generate negative test cases for the discount feature"):
        
        if not st.session_state['kb_built']:
            st.error("Please build the Knowledge Base in the sidebar first !!")
        else:
            # A. Append User Message to History
            st.session_state['messages'].append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.write(user_query)
            
            # B. Generate Response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        payload = {"query": user_query}
                        response = requests.post(f"{API_URL}/generate-tests", json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Store for Tab 2 logic
                            st.session_state['test_cases'] = data 
                            
                            # Append AI Response (Data) to History
                            st.session_state['messages'].append({"role": "assistant", "content": data})
                            
                            # Force a rerun so the history loop above renders this new message
                            st.rerun()
                        else:
                            st.error(f"Server Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

# --- TAB 2: Automation Engineer (Script Gen) ---
with tab2:
    st.subheader("Selenium Script Generator")
    
    # Ensure HTML content is retrieved safely
    html_safe = st.session_state.get('html_content', "")

    if not st.session_state['test_cases']:
        st.warning("⚠️ Please generate test cases in Tab 1 first.")
    elif not html_safe:
        st.warning("⚠️ Please provide HTML content in the Sidebar.")
    else:
        # Layout: Selection on Left, Code on Right
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("### Select Scenario")
            test_cases = st.session_state['test_cases']
            options = [f"{tc.get('Test_ID')} - {tc.get('Feature')}" for tc in test_cases]
            selected_idx = st.selectbox("Choose a test case to automate:", range(len(options)), format_func=lambda x: options[x])
            
            st.markdown("---")
            st.markdown("**Selected Scenario Details:**")
            selected_tc = test_cases[selected_idx]
            st.info(selected_tc.get('Test_Scenario'))
            
            if st.button("⚡ Generate Script", type="primary"):
                with st.spinner("Writing Python Selenium code..."):
                    try:
                        payload = {
                            "test_case": selected_tc,
                            "html_content": html_safe
                        }
                        res = requests.post(f"{API_URL}/generate-script", json=payload)
                        if res.status_code == 200:
                            st.session_state['generated_script'] = res.json().get("script")
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

        with c2:
            st.markdown("### Generated Python Code")
            if st.session_state['generated_script']:
                st.code(st.session_state['generated_script'], language="python")
                st.download_button(
                    "📥 Download Script", 
                    data=st.session_state['generated_script'], 
                    file_name="test_script.py", 
                    mime="text/x-python"
                )
            else:
                st.caption("Select a test case and click 'Generate Script' to see code here.")