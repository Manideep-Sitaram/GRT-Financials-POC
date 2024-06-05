from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv
import shutil
import os

# Load environment variables
load_dotenv()

# Set directory for vector database
PERSIST_DIRECTORY = 'db'

# Function to extract text from the uploaded PDF document
def get_text_documents(pdf_doc):
    with open(pdf_doc.name, mode='wb') as w:
        w.write(pdf_doc.getvalue())
    loader = PyPDFLoader(pdf_doc.name)
    text_documents = loader.load()
    return text_documents

# Function to split text documents into smaller chunks
def get_text_chunks(text_documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    text_chunks = text_splitter.split_documents(text_documents)
    return text_chunks

# Function to load text chunks into a FAISS vector database
def load_text_chunks_in_vector_database(text_chunks):
    db = FAISS.from_documents(text_chunks, OpenAIEmbeddings())
    db.save_local(PERSIST_DIRECTORY)

# Function to reset the vector database by removing the directory
def reset_vector_database():
    if os.path.isdir(PERSIST_DIRECTORY):
        shutil.rmtree(PERSIST_DIRECTORY)
        print("Vector database is removed")
    else:
        print("The database is already empty")

# Function to query the vector database with user input
def user_input(user_query):
    llm = ChatOpenAI(temperature=0.0)
    prompt = ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context.
        Think step by step before providing a detailed answer.
        I will tip you $1000 if the user finds the answer helpful.
        <context>
        {context}
        </context>
        Question: {input}
    """)
    document_chain = create_stuff_documents_chain(llm, prompt)
    db = FAISS.load_local(PERSIST_DIRECTORY, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    retriever = db.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    response = retrieval_chain.invoke({"input": user_query})
    return response["answer"]

# Function to load documents initially with predefined prompts
def load_documents_initially(pdf_doc):
    reset_vector_database()
    text_documents = get_text_documents(pdf_doc)
    text_chunks = get_text_chunks(text_documents)
    load_text_chunks_in_vector_database(text_chunks)
    
    # Predefined prompts
default_prompts =  [
    "What was the revenue for the last 2 years? Provide the answer in tabular format.",
    "What was the revenue for the last 2 quarters? Provide the answer in tabular format.",
    "What was the revenue by business lines? Provide the answer in tabular format.",
    "What was the revenue by geographic location? Provide the answer in tabular format.",
    "What is the summary of changes in revenue? Provide the answer in tabular format.",
    "What are the reasons for the changes in revenue? Provide the answer in commentary format.",
    "What was the net income for the last 2 years? Provide the answer in tabular format.",
    "What was the net income for the last 2 quarters? Provide the answer in tabular format.",
    "What was the net income by business lines? Provide the answer in tabular format.",
    "What was the net income by geographic location? Provide the answer in tabular format.",
    "What is the summary of changes in net income? Provide the answer in tabular format.",
    "What are the reasons for the changes in net income? Provide the answer in commentary format.",
    "What was the gross profit for the last 2 years? Provide the answer in tabular format.",
    "What was the gross profit for the last 2 quarters? Provide the answer in tabular format.",
    "What are the reasons for the changes in gross profit? Provide the answer in commentary format.",
    "What was the operating profit for the last 2 years? Provide the answer in tabular format.",
    "What was the operating profit for the last 2 quarters? Provide the answer in tabular format.",
    "What are the reasons for the changes in operating profit? Provide the answer in commentary format.",
    "What was the cash flow from operations (CFFO) for the last 2 years? Provide the answer in tabular format.",
    "What was the cash flow from operations (CFFO) for the last 2 quarters? Provide the answer in tabular format.",
    "What is the summary of changes in CFFO? Provide the answer in tabular format.",
    "What are the reasons for the changes in CFFO? Provide the answer in commentary format.",
    "What was the capital expenditure (CAPEX) for the last 2 years? Provide the answer in tabular format.",
    "What was the capital expenditure (CAPEX) for the last 2 quarters? Provide the answer in tabular format.",
    "What are the reasons for the changes in CAPEX? Provide the answer in commentary format.",
    "What was the cash flow from investing activities (CFFI) for the last 2 years/quarters? Provide the answer in tabular format.",
    "What are the reasons for the changes in CFFI? Provide the answer in commentary format.",
    "What was the cash flow from financing activities (CFFF) for the last 2 years/quarters? Provide the answer in tabular format.",
    "What are the reasons for the changes in CFFF? Provide the answer in commentary format.",
    "What are the reasons for the changes in working capital? Provide the answer in commentary format.",
    "What was the EBITDA for the last 2 years? Provide the answer in tabular format.",
    "What was the EBITDA for the last 2 quarters? Provide the answer in tabular format.",
    "What is the summary of changes in EBITDA? Provide the answer in tabular format.",
    "What are the reasons for the changes in EBITDA? Provide the answer in commentary format.",
    "What is the total liquidity? Provide the answer in tabular format.",
    "What was the liquidity for the previous and current year/quarter? Provide the answer in tabular format.",
    "What are the reasons for the changes in liquidity? Provide the answer in commentary format.",
    "What is the summary of recent events? Provide the answer in commentary format.",
    "What was the debt for the last 2 years? Provide the answer in tabular format.",
    "What was the debt for the last quarter with the last financial report? Provide the answer in tabular format.",
    "What is the summary of changes in debt? Provide the answer in tabular format.",
    "What are the reasons for the changes in debt? Provide the answer in commentary format.",
    "What were the changes in equity for the last 2 years? Provide the answer in tabular format.",
    "What were the changes in equity for the last quarter with the last financial report? Provide the answer in tabular format.",
    "What are the reasons for the changes in equity/net worth? Provide the answer in commentary format.",
    "What was the financial performance for the last quarter/financial year? Provide the answer in commentary format."
]

    # Generate initial question-and-answer pairs
    initial_question_and_answers = []
    for prompt in default_prompts:
        answer = user_input(prompt)
        initial_question_and_answers.append({"question": prompt, "answer": answer})
    
    return initial_question_and_answers
