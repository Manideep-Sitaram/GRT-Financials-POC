import streamlit as st
from model import *

st.title("GRT Financials Application")

# Sidebar menu
with st.sidebar:
    st.title("Menu")
    pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process",type="pdf")
    submit_process = st.button("Submit & Process")

user_query = st.text_input("Please Enter Your Query")

if user_query:
    st.write(user_input(user_query).replace("$","\$"))

if submit_process:
    if pdf_docs:
        with st.spinner("Processing..."):
            # Perform any processing needed here
            initial_question_and_answers = load_documents_initially(pdf_docs)
            st.write("Submit & Process is clicked")
            
            for qa_pair in initial_question_and_answers:
                question = qa_pair["question"]
                answer = (qa_pair["answer"]).replace("$","\$")
                st.write(f"**{question}**")
                st.write(f"**Response:**\n {answer}")
                st.write("---")  # This will add a horizontal line for better 
    else:
        st.warning("Please Upload The PDF")
