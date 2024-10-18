import os
import concurrent.futures
import pytesseract
from pdf2image import convert_from_path
from dotenv import load_dotenv
import torch
import gradio as gr
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, FewShotPromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY")
USER_MSDS_TXT = 'MSDS_text'

DEVICE = 'cuda:0' if torch.cuda.is_available() else 'cpu'

class DangerousGoodsAnalyzer:
    def __init__(self):
        self.llm_summarize = ChatGroq(groq_api_key=GROQ_API_KEY, model_name='Llama-3.1-70b-Versatile')
        self.llm_analyze = ChatGroq(groq_api_key=GROQ_API_KEY, model_name='Llama-3.1-70b-Versatile')

        self.summarize_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that can summarize material safety datasheet text",
                ),
                ("human", "summarize, shorten, and extract the key points of this material safety datasheet so that it can be analyzed based on IMDG guide, make sure your response is brief: {text} "),
            ]
        )

        self.analyze_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant THAT SPEAK INDONESIAN LANGUAGE who can classify a dangerous goods, determine the packaging strategy, what needs to be used to package it, and 'DECIDE' whether or not it can be loaded in the ship based on IMDG, and dont forget to format the response using HTML tag format such as <h>, <p>, <li>, etc. it is mandatory, you will be punished if you don't format it using html tag!!!",
                ),
                ("human", "based on this information, determine the classification, the packaging strategy to be used, and the package to be used briefly. and decide can it be loaded in the ship, it is mandatory to make the decision: \n{text}"),
            ]
        )
        self.summarize_chain = LLMChain(llm=self.llm_summarize, prompt=self.summarize_prompt)
        self.analyze_chain = LLMChain(llm=self.llm_analyze, prompt=self.analyze_prompt)

        self.chain = SimpleSequentialChain(chains=[self.summarize_chain, self.analyze_chain])

    def ocr_pdf(self, pdf_path, user_uuid):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            images = convert_from_path(pdf_path, dpi=350)
            text_list = list(executor.map(pytesseract.image_to_string, images))
        
        full_text =  " ".join(text_list).lower()

        print(full_text)
        if 'safety' not in full_text or 'keselamatan' not in full_text:
            return False
        
        user_txt = os.path.join(USER_MSDS_TXT, f'{user_uuid}.txt')
        
        if not os.path.exists(USER_MSDS_TXT):
            os.makedirs(USER_MSDS_TXT)

        with open(user_txt, 'w') as f:
            f.write(full_text)

    def process_document(self, text_file):
        final_result = self.chain.run({"input": text_file})
        return final_result


