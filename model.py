from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.output_parsers import StructuredOutputParser
import shutil
from dotenv import load_dotenv
import os
load_dotenv()

persist_directory = 'db'


def get_text_documents(pdf_doc):
    
    with open(pdf_doc.name, mode='wb') as w:
        w.write(pdf_doc.getvalue())
        
    loader=PyPDFLoader(pdf_doc.name)
    text_documents=loader.load()
        
    
    return text_documents


def get_text_chunks(text_documents):
    
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    text_chunks=text_splitter.split_documents(text_documents)
    
    return text_chunks

def load_text_chunks_in_vector_databse(text_chunks):
    db=FAISS.from_documents(text_chunks,OpenAIEmbeddings())
    db.save_local(persist_directory)


def user_input(user_query):

    llm=ChatOpenAI(temperature=0.0)
    prompt= ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context.
        Think step by step before providing on detailed answer.
        I will tip you $1000 if the user finds the answer helpful
        <context>
        {context}
        </context>
        Question: {input}
        """)
    document_chain=create_stuff_documents_chain(llm,prompt)
    db=FAISS.load_local("db",OpenAIEmbeddings(),allow_dangerous_deserialization=True)
    retriever=db.as_retriever()
    retrieval_chain=create_retrieval_chain(retriever,document_chain)
    response=retrieval_chain.invoke({"input": user_query})
    return response["answer"]


def reset_vector_database():
    if os.path.isdir(f'{persist_directory}'):
        shutil.rmtree(persist_directory)
        print("Chroma Database is removed")
        
    else:
        print("The Database is already empty")
    
def load_documents_initially(pdf_doc):
    reset_vector_database()
    text_documents = get_text_documents(pdf_doc)
    text_chunks = get_text_chunks(text_documents)
    load_text_chunks_in_vector_databse(text_chunks)
    
    default_prompts =  [
    "What was the revenue for the last 2 years? Provide the answer in tabular format.",
    "What was the revenue for the last 2 quarters? Provide the answer in tabular format.",
    "What was the revenue by business lines? Provide the answer in tabular format.",
    "What was the revenue by geographic location? Provide the answer in tabular format.",
    "What is the summary of changes in revenue? Provide the answer in tabular format.",
    "What are the reasons for the change in revenue? Provide the answer in commentary format.",
    "What was the net income for the last 2 years? Provide the answer in tabular format.",
    "What was the net income for the last 2 quarters? Provide the answer in tabular format.",
    "What was the net income by business lines? Provide the answer in tabular format.",
    "What was the net income by geographic location? Provide the answer in tabular format.",
    "What is the summary of changes in net income? Provide the answer in tabular format.",
    "What are the reasons for the change in net income? Provide the answer in commentary format.",
    "What was the gross profit for the last 2 years? Provide the answer in tabular format.",
    "What was the gross profit for the last 2 quarters? Provide the answer in tabular format.",
    "What are the reasons for the change in net income? Provide the answer in commentary format.",
    "What was the operating profit for the last 2 years? Provide the answer in tabular format.",
    "What was the operating profit for the last 2 quarters? Provide the answer in tabular format.",
    "What are the reasons for the change in net income? Provide the answer in commentary format.",
    "What was the cash flow from operations (CFFO) for the last 2 years? Provide the answer in tabular format.",
    "What was the cash flow from operations (CFFO) for the last 2 quarters? Provide the answer in tabular format.",
    "What is the summary of changes in CFFO? Provide the answer in tabular format.",
    "What are the reasons for the change in CFFO? Provide the answer in commentary format.",
    "What was the capital expenditure (CAPEX) for the last 2 years? Provide the answer in tabular format.",
    "What was the capital expenditure (CAPEX) for the last 2 quarters? Provide the answer in tabular format.",
    "What are the reasons for the change in CAPEX? Provide the answer in commentary format.",
    "What was the cash flow from investing activities (CFFI) for the last 2 years/quarters? Provide the answer in tabular format.",
    "What are the reasons for the change in CFFI? Provide the answer in commentary format.",
    "What was the cash flow from financing activities (CFFF) for the last 2 years/quarters? Provide the answer in tabular format.",
    "What are the reasons for the change in CFFF? Provide the answer in commentary format.",
    "What are the reasons for the change in working capital? Provide the answer in commentary format.",
    "What was the EBITDA for the last 2 years? Provide the answer in tabular format.",
    "What was the EBITDA for the last 2 quarters? Provide the answer in tabular format.",
    "What is the summary of changes in EBITDA? Provide the answer in tabular format.",
    "What are the reasons for the change in EBITDA? Provide the answer in commentary format.",
    "What is the total liquidity? Provide the answer in tabular format.",
    "What was the liquidity for the previous and current year/quarter? Provide the answer in tabular format.",
    "What are the reasons for the change in liquidity? Provide the answer in commentary format.",
    "What is the summary of recent events? Provide the answer in commentary format.",
    "What was the debt for the last 2 years? Provide the answer in tabular format.",
    "What was the debt for the last quarter with the last financial report? Provide the answer in tabular format.",
    "What is the summary of changes in debt? Provide the answer in tabular format.",
    "What are the reasons for the change in debt? Provide the answer in commentary format.",
    "What were the changes in equity for the last 2 years? Provide the answer in tabular format.",
    "What were the changes in equity for the last quarter with the last financial report? Provide the answer in tabular format.",
    "What are the reasons for the changes in equity/net worth? Provide the answer in commentary format.",
    "What was the financial performance for the last quarter/financial year? Provide the answer in commentary format."
]

    
    initial_question_and_answers = []
    for prompt in default_prompts:
        question_and_answer = {}
        question_and_answer["question"] = prompt
        question_and_answer["answer"] = user_input(prompt)
        
        initial_question_and_answers.append(question_and_answer)
    
    return initial_question_and_answers
    