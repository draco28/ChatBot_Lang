from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Middleware Assistant Chatbot"
    debug: bool = False
    log_level: str = "INFO"
    
    host: str = "0.0.0.0"
    port: int = 8000

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_temperature: float = 0.0

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "documents"

    
    ws_ping_interval: int = 30
    session_timeout: int = 3600
    
    agent_max_iterations: int = 5
    memory_window_size: int = 10
    
    rag_chunk_size: int = 600
    rag_chunk_overlap: int = 80
    rag_top_k: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()