"""
Configuration management
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    """
    Application configuration loaded from environment variables
    """

    # GLM API
    glm_api_key: str
    glm_api_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    glm_model: str = "glm-4-flash"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "agent-system"

    # PostgreSQL (for future use)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "hive_five"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    # Redis (for future use)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # System
    log_level: str = "INFO"
    environment: str = "development"
    agent_response_timeout: int = 30
    max_context_events: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False
