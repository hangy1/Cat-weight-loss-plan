"""Configuration management"""
import json
import os
from pathlib import Path
from typing import Dict, Any


class Settings:
    """Application settings"""

    def __init__(self):
        self.PROJECT_NAME = "Cat Calorie Calculator API"
        self.VERSION = "1.0.0"
        self.DESCRIPTION = "Calculate daily calorie requirements for cats based on weight, life stage, and weight goals"

        # CORS settings
        self.CORS_ORIGINS = [
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ]

        # Database settings
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://localhost/cat_calorie_db"
        )

        # Load calculation config
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        config_path = Path(__file__).parent.parent.parent / "config.json"
        with open(config_path, "r") as f:
            return json.load(f)

    @property
    def life_stage_factors(self) -> Dict[str, float]:
        """Get life stage factors"""
        return self.config_data["life_stage_factors"]

    @property
    def activity_adjustment(self) -> Dict[str, Dict[str, Any]]:
        """Get activity adjustment factors"""
        return self.config_data["activity_adjustment"]

    @property
    def constants(self) -> Dict[str, Any]:
        """Get constants"""
        return self.config_data["constants"]


# Create settings instance
settings = Settings()
