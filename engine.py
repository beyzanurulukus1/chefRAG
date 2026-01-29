import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

class ChefRAGEngine:
    def __init__(self, k_val=3):
        # Bileşenleri başlat
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = Chroma(persist_directory="./chroma_db", embedding_function=self.embeddings)
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": k_val})
        
        # LLM Yapılandırması (Temperature sabit 0.7)
        self.llm = ChatGroq(
            temperature=0.7,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Prompt Tasarımı
        self.template = """Sen uzman bir aşçısın. Aşağıdaki bağlamı ve geçmişi kullanarak yardımcı ol.
        BAĞLAM: {context}
        GEÇMİŞ: {chat_history}
        SORU: {question}
        CEVAP:"""
        self.prompt = ChatPromptTemplate.from_template(self.template)

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def get_chain(self):
        # LCEL Zinciri oluşturma
        chain = (
            {
                "context": (lambda x: x["question"]) | self.retriever | self.format_docs,
                "question": lambda x: x["question"],
                "chat_history": lambda x: x["chat_history"]
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        return chain