import streamlit as st
from model import load_documents_initially, user_input, reset_vector_database
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Override default sqlite3 with pysqlite3 for better performance
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Set environment variables for LangChain and OpenAI APIs
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]

# Streamlit application title
st.title("GRT Financials Application")

# Sidebar menu for file upload and processing
with st.sidebar:
    st.title("Menu")
    pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process", type="pdf")
    submit_process = st.button("Submit & Process")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Text input for user queries
user_query = st.text_input("Please Enter Your Query")

# Function to process user query and update chat history
def process_user_query(query):
    response = user_input(query).replace("$", "\$")
    st.session_state.chat_history.append({"user": query, "bot": response})

# Process user query if entered
if user_query:
    process_user_query(user_query)

# Process uploaded PDF document
if submit_process:
    if pdf_docs:
        with st.spinner("Processing..."):
            reset_vector_database()
            initial_question_and_answers = load_documents_initially(pdf_docs)
            for qa_pair in initial_question_and_answers:
                question = qa_pair["question"]
                answer = qa_pair["answer"].replace("$", "\$")
                st.session_state.chat_history.append({"user": question, "bot": answer})
    else:
        st.warning("Please Upload The PDF")

# Display chat history
for chat in st.session_state.chat_history:
    st.markdown(f"**User:** {chat['user']}")
    st.markdown(f"**Bot:** {chat['bot']}")
    st.write("---")  # Horizontal line for separation
