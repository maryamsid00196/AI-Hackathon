import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)  # Optional custom base URL
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Application settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Skill standards matrix
    SKILL_STANDARDS: Dict[str, Dict[str, str]] = {
        "HTML": {
            "Junior": "Basic",
            "Senior": "Intermediate",
            "Team Lead": "Expert"
        },
        "CSS": {
            "Junior": "Basic",
            "Senior": "Expert",
            "Team Lead": "Expert"
        },
        "JavaScript": {
            "Junior": "Basic",
            "Senior": "Expert",
            "Team Lead": "Expert"
        },
        "React": {
            "Junior": "Basic",
            "Senior": "Expert",
            "Team Lead": "Expert"
        },
        "Next.js": {
            "Junior": "Basic",
            "Senior": "Expert",
            "Team Lead": "Expert"
        },
        "Git Basics": {
            "Junior": "Basic",
            "Senior": "Advanced",
            "Team Lead": "Expert"
        },
        "Debugging Skills": {
            "Junior": "Basic",
            "Senior": "Expert",
            "Team Lead": "Expert"
        },
        "API Integration": {
            "Junior": "Basic",
            "Senior": "Intermediate",
            "Team Lead": "Expert"
        },
        "State Management (Redux/Zustand)": {
            "Junior": "Basic",
            "Senior": "Intermediate",
            "Team Lead": "Expert"
        },
        "Performance Optimization": {
            "Junior": "Basic",
            "Senior": "Intermediate",
            "Team Lead": "Expert"
        }
    }
    
    # Proficiency levels (ordered)
    PROFICIENCY_LEVELS: List[str] = [
        "None",
        "Basic",
        "Intermediate",
        "Advanced",
        "Expert"
    ]
    
    # Conversation settings
    MAX_CONVERSATION_TURNS = 8  # Maximum messages before auto-ending conversation
    MIN_CONVERSATION_TURNS = 3  # Minimum exchanges before AI can end conversation
    CONVERSATION_TEMPERATURE = 0.7
    
    # Assessment settings
    MIN_QUESTIONS_PER_SKILL = 2
    CONFIDENCE_WEIGHT = 0.3


config = Config()

