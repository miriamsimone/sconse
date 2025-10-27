"""
Configuration settings for the AI microservice
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    BRAVE_API_KEY: str = os.getenv("BRAVE_API_KEY", "")
    FIREBASE_SERVICE_ACCOUNT: str = os.getenv("FIREBASE_SERVICE_ACCOUNT", "")
    
    # OpenAI Configuration
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    
    # Basic Pitch Configuration
    BASIC_PITCH_MODEL_PATH: str = os.getenv("BASIC_PITCH_MODEL_PATH", "")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sconces AI Microservice"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
    ]
    
    # Audio Processing
    MAX_AUDIO_DURATION: int = 30  # seconds
    SUPPORTED_AUDIO_FORMATS: list = ["wav", "mp3", "m4a"]
    
    # IMSLP Configuration
    IMSLP_BASE_URL: str = "https://imslp.org/api.php"
    MUTOPIA_BASE_URL: str = "https://www.mutopiaproject.org"
    
    # Firebase Configuration
    FIREBASE_STORAGE_BUCKET: str = os.getenv("FIREBASE_STORAGE_BUCKET", "")
    
    def __init__(self):
        """Validate required settings"""
        # No required settings - all are optional for now
        pass

# Create global settings instance
settings = Settings()
