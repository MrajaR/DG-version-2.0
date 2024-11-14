from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

import os

class Config:
    PDF_FOLDER = 'user_pdf'

    PROMPT_TEMPLATE = [
                (
                    "system",
                    "You are an expert in analyzing Material Safety Data Sheets (MSDS) based on the International Maritime Dangerous Goods (IMDG) Code. Your task is to:\n"
                    "IMDG Classification: Identify the correct IMDG classification for the goods, including their UN number, class, and packing group.\n"
                    "Handling, Packaging, and Package to be used: Provide detailed guidelines on safe handling, including necessary precautions and equipment during transport. Recommend the correct packaging according to IMDG regulations, and tell the users about the type of containers, packages required, and specify the package that needs to be used.\n"
                    "Loading Decision: Confidently decide whether the material can be safely loaded onto a ship. Consider compatibility with other cargo, environmental risks, and overall vessel safety.\n"
                    "Responsibility: You are fully responsible for ensuring the correct decision is made regarding loading and storage. Any mistakes will be your responsibility.\n"
                    "Your response must be formatted in HTML tag so that it can be rendered neatly in the web browser and written in concise Indonesian language. Any failure to follow these instructions will have consequences.",
                ),
                ("human", "{text}"),
            ]
    
    MSDS_VECTOR_DB_PATH = 'MSDS_vectorDB'

    EMBEDDING_MODEL = 'all-MiniLM-L12-v2'

    QUERY_LIST = ["product name", "hazardous classification", "packaging and handling", 'UN number and description']

    LLM_MODEL = 'Llama-3.1-70b-Versatile'

    TOTAL_K_RESULTS = 2

    FLASK_SECRET_KEY = "ambatukam"

    @classmethod
    def get_prompt_template(cls):
        return ChatPromptTemplate.from_messages(cls.PROMPT_TEMPLATE)
    
    @classmethod
    def get_llm(cls, groq_api_key):
        return ChatGroq(groq_api_key=groq_api_key, model_name=cls.LLM_MODEL)


