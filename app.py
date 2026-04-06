# ===================================================================
# Libraries
# ===================================================================

from typing import Iterable
import re, os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import MongoDBAtlasVectorSearch

# ===================================================================
# CONFIGURATION
# ===================================================================

class Config:
    # Removed Airtable configurations
    URI = os.getenv("MONGODB_URI")
    CERTIFICATE_PATHWAY = "mad_cert.pem"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    ENDPOINT = "https://models.github.ai/inference"
    MODEL_NAME = "gpt-4o"
    EMBEDDINGS_MODEL = "text-embedding-3-small"

# ===================================================================
# AI MANAGER (LLM & Embeddings)
# ===================================================================

class AIMANAGER:
    """ AI MANAGER FOR THE OPENAI MODELS """
    @staticmethod
    def initialize_models(model_name: str = Config.MODEL_NAME, embeddings_model_name: str = Config.EMBEDDINGS_MODEL, temperature: float = 0.7) -> tuple:
        try:
            llm = ChatOpenAI(
                model=model_name,
                openai_api_key=Config.GITHUB_TOKEN,
                openai_api_base=Config.ENDPOINT,
                temperature=temperature,
                top_p=0.95,
                streaming=True
            )
            
            embeddings = OpenAIEmbeddings(
                model=embeddings_model_name,
                openai_api_key=Config.GITHUB_TOKEN,
                openai_api_base=Config.ENDPOINT
            )
            return llm, embeddings
        
        except Exception as e:
            raise RuntimeError(f"AI Manager Error: {str(e)}")

    @staticmethod
    def get_prompt() -> ChatPromptTemplate:
        system_message = """أنت مستشار عقاري خبير في مدينتي. هدفك الأول هو مساعدة العميل بلهجة مصرية بيعية محترفة.
            التعليمات البيعية :
            1. لو طلب العميل متوفر اعرض تفاصيل الشقة بالكامل ( المساحة , السعر الاجمالي, الاوفر, المدفوع, مده التقسيط, الاستلام)
            2. البديل الأقرب: إذا لم تجد طلب العميل، اقترح أقرب وحدات من السياق (2-3 وحدات) واعرض تفاصيلها بالكامل.
            3. قارن بين الوحدات المختارة من حيث المميز في كل واحدة فيهم.
            4. الأمانة: شجع العميل على المتاح حالياً لأن "الفرص بتخلص بسرعة".
            5. ممنوع استعمال bullet points.
            6. الختام: اختم دائماً برقم التواصل: 0106."""
        
        human_message = """إليك الوحدات المتاحة حالياً (السياق):
            {context}
            سؤال العميل: {query}"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])

# ===================================================================
# VECTOR DATABASE MANAGER 
# ===================================================================

class DatabaseManager:
    """ Handles data operations for MongoDB Atlas """

    @staticmethod
    def _get_client() -> MongoClient:
        try:
            return MongoClient(
                Config.URI,
                tls=True,
                tlsCertificateKeyFile=Config.CERTIFICATE_PATHWAY, 
                server_api=ServerApi('1')
            )
        except Exception as e:
            raise RuntimeError(f"MongoDB Connection Error: {str(e)}")

    @staticmethod
    def get_vector_store() -> MongoDBAtlasVectorSearch:
        """ Establishes a connection to the existing MongoDB Atlas Vector Store. """
        try:
            _, embeddings = AIMANAGER.initialize_models()

            client = DatabaseManager._get_client()
            db = client["RealEstate_RAG_OpenAI"]
            collection = db["available_units"]

            return MongoDBAtlasVectorSearch(
                collection=collection,
                embedding=embeddings,
                index_name="vector_index"
            )
        
        except Exception as e:
            raise RuntimeError(f"Vector Store Connection Error: {str(e)}")

# ===================================================================
# CHAT LOGIC
# ===================================================================

def ask_real_estate_bot(user_query: str) -> Iterable[str]:
    """ Retrieves data directly from MongoDB and streams the AI response. """
    try:
        model, _ = AIMANAGER.initialize_models()
        prompt_template = AIMANAGER.get_prompt()
        vector_db = DatabaseManager.get_vector_store()

        if not all([model, prompt_template, vector_db]):
            yield "عذراً، واجهت مشكلة في الاتصال بقاعدة البيانات."
            return
        
        # Perform similarity search on existing MongoDB data
        docs = vector_db.similarity_search(user_query, k=5)
        
        if not docs:
            yield "لم أتمكن من العثور على وحدات تطابق طلبك حالياً في قاعدة البيانات."
            return
        
        full_context = "\n\n".join([doc.page_content for doc in docs])
        chain = prompt_template | model
        
        for chunk in chain.stream({"context": full_context, "query": user_query}):
            if chunk.content:  
                yield chunk.content
    
    except Exception as e:
        print(f"Error: {str(e)}")
        yield "حدث خطأ أثناء البحث في الوحدات المتاحة."
