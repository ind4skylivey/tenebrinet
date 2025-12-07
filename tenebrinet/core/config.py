# tenebrinet/core/config.py
import os
import re
import yaml
from typing import Literal, List, Optional
from pydantic import BaseModel, Field

# --- Pydantic Models ---

class SSHServiceConfig(BaseModel):
    enabled: bool = True
    port: int = 2222
    host: str = "0.0.0.0"
    banner: str = "OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"
    max_connections: int = 100
    timeout: int = 30

class HTTPServiceConfig(BaseModel):
    enabled: bool = True
    port: int = 8080
    host: str = "0.0.0.0"
    fake_cms: str = "WordPress 5.8"
    serve_files: bool = True

class FTPServiceConfig(BaseModel):
    enabled: bool = True
    port: int = 2121
    host: str = "0.0.0.0"
    anonymous_allowed: bool = True

class ServicesConfig(BaseModel):
    ssh: SSHServiceConfig
    http: HTTPServiceConfig
    ftp: FTPServiceConfig

class DatabaseConfig(BaseModel):
    url: str 
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

class RedisConfig(BaseModel):
    url: str

class MLConfig(BaseModel):
    model_path: str = "data/models/threat_classifier.joblib"
    retrain_interval: str = "24h"
    confidence_threshold: float = 0.7
    features: List[str] = Field(default_factory=list)

class AbuseIPDBConfig(BaseModel):
    enabled: bool = True
    api_key: str
    check_on_connect: bool = True

class VirusTotalConfig(BaseModel):
    enabled: bool = False
    api_key: Optional[str] = None

class ThreatIntelConfig(BaseModel):
    abuseipdb: AbuseIPDBConfig
    virustotal: VirusTotalConfig

class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["json", "console"] = "json"
    output: str = "data/logs/tenebrinet.log"
    rotation: str = "100 MB"

class TenebriNetConfig(BaseModel):
    services: ServicesConfig
    database: DatabaseConfig
    redis: RedisConfig
    ml: MLConfig
    threat_intel: ThreatIntelConfig
    logging: LoggingConfig

# --- Loader Logic ---

# Regex for ${VAR_NAME} or ${VAR_NAME:default}
ENV_VAR_PATTERN = re.compile(r'\$\{(\w+)(?::([^}]*))?\}')

def substitute_env_vars(content: str) -> str:
    """
    Substitutes environment variables in the format ${VAR} or ${VAR:default}.
    """
    def replace(match):
        var_name = match.group(1)
        default_value = match.group(2)
        return os.environ.get(var_name, default_value if default_value is not None else "")
    
    return ENV_VAR_PATTERN.sub(replace, content)

def load_config(config_path: str = "config/honeypot.yml") -> TenebriNetConfig:
    """
    Loads the configuration from a YAML file, substitutes environment variables,
    and validates it against the Pydantic schema.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, 'r') as f:
        raw_content = f.read()

    # Substitute environment variables
    processed_content = substitute_env_vars(raw_content)

    # Parse YAML
    try:
        config_dict = yaml.safe_load(processed_content)
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {e}")

    # Validate with Pydantic
    try:
        config = TenebriNetConfig(**config_dict)
        return config
    except Exception as e:
        raise ValueError(f"Invalid configuration: {e}")
