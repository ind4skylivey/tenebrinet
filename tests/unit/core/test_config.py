# tests/unit/core/test_config.py
import pytest
import os
from tenebrinet.core.config import (
    load_config, substitute_env_vars, TenebriNetConfig
)


@pytest.fixture
def valid_config_yaml(tmp_path):
    config_content = """
services:
  ssh:
    enabled: true
    port: 2222
    host: "0.0.0.0"
    banner: "OpenSSH_Test"
    max_connections: 50
    timeout: 15
  http:
    enabled: true
    port: 8080
    host: "0.0.0.0"
    fake_cms: "WP Test"
    serve_files: false
  ftp:
    enabled: false
    port: 2121
    host: "127.0.0.1"
    anonymous_allowed: false

database:
  url: "postgresql+asyncpg://user:pass@localhost/db"
  pool_size: 5
  max_overflow: 10
  echo: true

redis:
  url: "redis://localhost:6379/0"

ml:
  model_path: "models/test.joblib"
  retrain_interval: "12h"
  confidence_threshold: 0.8
  features: ["f1", "f2"]

threat_intel:
  abuseipdb:
    enabled: true
    api_key: "test_abuse_key"
    check_on_connect: true
  virustotal:
    enabled: false
    api_key: null

logging:
  level: "DEBUG"
  format: "console"
  output: "logs/test.log"
  rotation: "50 MB"
"""
    config_file = tmp_path / "honeypot.yml"
    config_file.write_text(config_content)
    return str(config_file)


def test_load_valid_config(valid_config_yaml):
    config = load_config(valid_config_yaml)
    assert isinstance(config, TenebriNetConfig)
    assert config.services.ssh.port == 2222
    assert config.services.ftp.enabled is False
    assert config.database.pool_size == 5
    assert config.logging.level == "DEBUG"


def test_env_var_substitution(tmp_path):
    config_content = """
services:
  ssh:
    enabled: true
    port: ${SSH_PORT:2222}
    host: "0.0.0.0"
    banner: "Banner"
    max_connections: 100
    timeout: 30
  http:
    enabled: true
    port: 8080
    host: "0.0.0.0"
    fake_cms: "CMS"
    serve_files: true
  ftp:
    enabled: true
    port: 2121
    host: "0.0.0.0"
    anonymous_allowed: true
database:
  url: "${DB_URL}"
  pool_size: 10
  max_overflow: 20
  echo: false
redis:
  url: "redis://localhost"
ml:
  features: []
threat_intel:
  abuseipdb:
    api_key: "key"
  virustotal:
    api_key: null
logging:
  level: "INFO"
  format: "json"
  output: "log.log"
  rotation: "100 MB"
"""
    config_file = tmp_path / "env_config.yml"
    config_file.write_text(config_content)

    # Set env vars
    os.environ["SSH_PORT"] = "2223"
    os.environ["DB_URL"] = "sqlite:///test.db"

    try:
        config = load_config(str(config_file))
        assert config.services.ssh.port == 2223
        assert config.database.url == "sqlite:///test.db"
    finally:
        # Cleanup
        if "SSH_PORT" in os.environ:
            del os.environ["SSH_PORT"]
        if "DB_URL" in os.environ:
            del os.environ["DB_URL"]


def test_env_var_default_value(tmp_path):
    # Test extracting default value when env var is missing
    content = "port: ${MISSING_VAR:8080}"
    result = substitute_env_vars(content)
    assert result == "port: 8080"


def test_invalid_config_structure(tmp_path):
    config_file = tmp_path / "invalid.yml"
    # This is invalid YAML syntax that causes a parser error
    config_file.write_text("invalid: yaml: content")

    # Match either YAML parser error OR Pydantic validation error
    with pytest.raises(
        ValueError,
        match="(Invalid configuration|Error parsing YAML configuration)"
    ):
        load_config(str(config_file))


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("non_existent_file.yml")
