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
import logging
from pptx import Presentation
from pypdf import PdfMerger
import time

# Configure logging
logging.basicConfig(
    filename='app.log',  # Log file name
    level=logging.INFO,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s %(levelname)s %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)

# Create a logger
logger = logging.getLogger(__name__)

load_dotenv()

persist_directory = 'db'

def get_pagenumbers_pretty_format(pagenumber_objects_list):
    res={}
    for pagenumber_object in  pagenumber_objects_list:
        for doc_name,pagenumber in pagenumber_object.items():
            if doc_name in res and pagenumber not in res[doc_name]:
                res[doc_name].append(pagenumber)
            else:
                res[doc_name] = [pagenumber]
                
    return res


def get_text_documents(pdf_doc):
    
    start_time = time.time()
    
    with open(pdf_doc.name, mode='wb') as w:
        w.write(pdf_doc.getvalue())
        
    loader=PyPDFLoader(pdf_doc.name)
    text_documents=loader.load()
    end_time = time.time()
    
    print(f" The taken taken to get Text Documents {end_time - start_time}")
    
    return text_documents


def get_text_chunks(text_documents):
    
    start_time = time.time()
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    text_chunks=text_splitter.split_documents(text_documents)
    
    return text_chunks

def load_text_chunks_in_vector_databse(text_chunks):
    db=FAISS.from_documents(text_chunks,OpenAIEmbeddings())
    db.save_local(persist_directory)


def user_input(user_query):

    logging.info(f"Getting user query: {user_query}")

    llm=ChatOpenAI(model="gpt-4o-mini",temperature=0.0, max_tokens=4096)
    prompt= ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context. Use current year as 2023.
        Think step by step before providing on detailed answer.
        I will tip you $1000 if the user finds the answer helpful
        <context>
        {context}
        </context>
        Question: {input}
        """)
    document_chain=create_stuff_documents_chain(llm,prompt)
    
    db=FAISS.load_local("db",OpenAIEmbeddings(),allow_dangerous_deserialization=True)
    relevant_docs_with_similarity_score = db.similarity_search_with_relevance_scores(user_query, k=4)
    relevant_docs = [ doc[0] for doc in relevant_docs_with_similarity_score]
    response = document_chain.invoke({
      "input": user_query,
      "context": relevant_docs
  })
    page_numbers = [doc[0].metadata["page"] for doc in relevant_docs_with_similarity_score if doc[1] > 0.70]
    page_numbers_with_source_name = [{doc[0].metadata["source"]:doc[0].metadata["page"]} for doc in relevant_docs_with_similarity_score if doc[1] > 0.70]
    page_numbers = list(set(page_numbers))
    response_object = {
        "response":response,
        # "pageNumbers":page_numbers,
        "pageNumbersWithSourceName": page_numbers_with_source_name,
        "prettyPageNumberFormat": get_pagenumbers_pretty_format(page_numbers_with_source_name)
        }
    return response_object


def reset_vector_database():
    start_time = time.time()
    if os.path.isdir(f'{persist_directory}'):
        shutil.rmtree(persist_directory)
        print("Chroma Database is removed")
        
    else:
        print("The Database is already empty")
    end_time = time.time()
    
    print(f"Resetting of Database took {end_time-start_time}")

    
def load_documents_initially(pdf_docs):
    reset_vector_database()
    print(f"The length of the PDF DOCS {len(pdf_docs)}")
    text_chunks =[]
    for pdf_doc in pdf_docs:  
        text_documents = get_text_documents(pdf_doc)
        text_chunks += get_text_chunks(text_documents)
    load_text_chunks_in_vector_databse(text_chunks)
    
    default_prompts =  [
        ("Company Overview", "Provide the company overview in about 200 words"),
        ("Company Overview", "Provide the company's segments overview. Provide commentary of the changes in segment performance with the previous year."),
        ("Company Overview", "What are the revenue generating product lines and how they individually performed in current year. Please provide results in a tabular format."),
        ("Company Overview", "What was the revenue by geographic location? Provide the answer in tabular format."),
        ("Company Overview", "Provide material events for the current year including acquisitions, divestitures, spin-offs, dividends, share repurchases - where dollar value is more than $500 million"),
        ("Senior Management", "Provide names of senior management and their designations, as bullet points"),
        ("Senior Management", "Provide background of the chief executive officer of the company"),
        ("Profit & Loss", "Provide in about 300 words commentary about the summary of changes in the current year vs the previous year for revenue or sales, gross profit, gross profit margin, operating profit, net profit, interst expenses, cash flow from operations with top two reasons for each"),
        ("Profit & Loss", "Provide a table of all profit & loss statement of current year starting with net sales and ending with net income and the previous year details for the same items."),
        ("Profit & Loss", "Provide EBITDA calculation for current year in tabular format and add previous year numbers for the same items"),
        ("Balance Sheet", "Provide a list of all balance sheet items including items under current assets, non-current assets, current liabilities, non-current liabilities and equity for both the current year and previous year in a tabular format"),
        ("Balance Sheet", "How much of the total debt is to be repaid in the next one year and can the company pay this from its liquidity. Please provide commentary"),
        ("Balance Sheet", "Provide a summary of changes in networth and debt for the current year against previous year"),
        ("Balance Sheet", "What are the amounts of credit facilities of the company and their expiry dates. Please provide commentary"),
        ("Balance Sheet", "Provide the debt repayment schedule for the company in a tabular format")
    ]

    
    initial_question_and_answers = []

    for prompt in default_prompts:
        question_and_answer = {}
        question_and_answer["category"], question_and_answer["question"] = prompt
        response_object = user_input(prompt[1])
        question_and_answer["answer"] = response_object["response"]
        question_and_answer["pageNumbersWithSourceName"]=response_object["pageNumbersWithSourceName"]
        question_and_answer["prettyPageNumberFormat"]=response_object["prettyPageNumberFormat"]
        
        initial_question_and_answers.append(question_and_answer)

    logging.info(f"Initial question and answers: {initial_question_and_answers}")
    
    return initial_question_and_answers