import pytest

import main


def test_get_token_exits_when_token_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr(main, "load_dotenv", lambda: None)

    with pytest.raises(SystemExit):
        main.get_token()


def test_get_token_returns_token_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "load_dotenv", lambda: None)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")

    assert main.get_token() == "fake-token"
