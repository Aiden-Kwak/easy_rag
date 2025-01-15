import os
from dotenv import load_dotenv
from .embedding import Embedding
from .retriever import Retriever
from .index import IndexManager # faiss index 이걸로 관리하자
from .agent import Agent

class RagService:
    def __init__(
            self,
            embedding_model="text-embedding-3-small",
            response_model="deepseek-chat",
            open_api_key=None,
            deepseek_api_key=None,
            deepseek_base_url="https://api.deepseek.com",
    ):
        load_dotenv()

        # set keys
        self.open_api_key = open_api_key or os.getenv("OPENAI_API_KEY")
        self.deepseek_api_key = deepseek_api_key or os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = deepseek_base_url

        # init module
        self.index_manager = IndexManager()
        self.embedding = Embedding(api_key=self.open_api_key, model=embedding_model)
        self.retriever = Retriever(self.embedding)
        self.agent = Agent(
            model=response_model,
            open_api_key=self.open_api_key,
            deepseek_api_key=self.deepseek_api_key,
            deepseek_base_url=self.deepseek_base_url,
        )

        # validation
        self.validate_configuration()
    
    def validate_configuration(self):
        if not self.open_api_key:
            raise ValueError("OPEN_API_KEY is required")
        if self.agent.model == "deepseek-chat" and not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is required for deepseek-chat model")
    
    def rsc(self, resource_path, index_file="faiss_index.bin", metadata_file="metadata.json", force_update=False):
        ###리소스 로드하고 임베딩 생성해야해. 
        ## 패스 아래의 모든 자료를 읽되, 메타데이터에서 이들 자료를 구분해야해
        if not force_update:
            index, metadata = self.index_manager.load(index_file, metadata_file)
            if index and metadata:
                return index, metadata

        index, metadata = self.retriever.load_resources(resource_path)
        self.index_manager.save(index, metadata, index_file, metadata_file)
        return index, metadata

    
    def generate_response(self, resource, query):
        ### 입력쿼리에 대해 응답생성해야해
        return self.agent.generate_response(resource, query)