import pytest
from pydantic import ValidationError

from workpilot.config import Settings


def test_reads_values_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")
    monkeypatch.setenv("WORKPILOT_MODEL", "claude-haiku-5-5")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.anthropic_api_key.get_secret_value() == "sk-test-123"
    assert settings.workpilot_model == "claude-haiku-5-5"


def test_model_has_a_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")
    monkeypatch.delenv("WORKPILOT_MODEL", raising=False)

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.workpilot_model == "claude-opus-5-5"


def test_missing_api_key_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)  # type: ignore[call-arg]


def test_api_key_is_hidden_when_printed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert "sk-test-123" not in repr(settings)
