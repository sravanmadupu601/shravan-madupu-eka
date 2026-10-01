import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def test_local_defaults_use_next_port_and_loopback_urls():
    config = Settings(_env_file=None)
    assert config.mcp_service_host == "127.0.0.1"
    assert config.mcp_service_port == 8005
    assert config.rag_service_url == "http://127.0.0.1:8003"
    assert config.document_service_url == "http://127.0.0.1:8000"


def test_remote_service_urls_are_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, rag_service_url="https://example.test")


def test_credentials_in_service_urls_are_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, document_service_url="http://user:pass@127.0.0.1:8000")


def test_non_loopback_bind_is_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, mcp_service_host="0.0.0.0")
