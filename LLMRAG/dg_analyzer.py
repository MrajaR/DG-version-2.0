import torch
import chromadb
from chromadb.utils import embedding_functions
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .utils import Extractor, CheckChromadb
from dotenv import load_dotenv
from config import Config
import os

load_dotenv()

class DangerousGoodsAnalyzer:
    def __init__(self):
        self.llm_analyze = Config.get_llm(os.getenv('GROQ_API_KEY'))

        self.analyze_prompt = Config.get_prompt_template()

        self.analyze_chain = self.analyze_prompt | self.llm_analyze

        self.client = chromadb.PersistentClient(path=Config.MSDS_VECTOR_DB_PATH)
        self.embeddings_for_chroma = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=Config.EMBEDDING_MODEL
        )
        self.collection = None

    def process_document(self, file_path, user_uuid):
        full_text = Extractor(file_path).parse_elements()

        docs = self.format_and_split(full_text)
        self.save_to_chroma(docs, user_uuid)

    def format_and_split(self, text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=300
        )
        text_chunks = text_splitter.create_documents([text])

        documents = [Document(page_content=chunk.page_content, metadata={"page": page}) for page, chunk in enumerate(text_chunks)]

        return documents
        
    def save_to_chroma(self, documents, user_uuid):
        CheckChromadb()

        if user_uuid not in [x.name for x in self.client.list_collections()]:
            print('Collection has not been created, hence create new collection')
        else:
            print('Collection has already been created, used existing collection')

        self.collection = self.client.get_or_create_collection(
            f"{user_uuid}",
            embedding_function=self.embeddings_for_chroma
        )

        self.collection.add(
            documents=[x.page_content for x in documents],
            ids=[str(x.metadata["page"]+1) for x in documents])
        
    def get_relevant_chunks(self):
        results = self.collection.query(
                query_texts=Config.QUERY_LIST, # Chroma will embed this for you
                n_results=Config.TOTAL_K_RESULTS, # how many results to return
                include=["documents"]
        )

        full_text = "Analyze based on this following context: \n\n"  # Add this phrase once at the beginning

        for i, text in enumerate(results['documents']):
            full_text += f"Context {i+1}:\n\n{text[0]}\n{text[1]}\n\n"

        # After the loop, print the full concatenated text
        return full_text

        
    def get_llm_response(self, text):        
        return self.analyze_chain.invoke({'text' : text}).content
    
    def delete_documents(self):
        self.collection.delete(ids=self.collection.get()['ids'])



