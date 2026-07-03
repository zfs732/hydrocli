from __future__ import annotations

from typer.testing import CliRunner

from hydro_cli.cli import app
from hydro_cli.config import Config, ConfigStore


def test_config_set_url_clears_current_contest(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HYDRO_CLI_CONFIG_DIR", str(tmp_path))
    store = ConfigStore()
    store.save(Config(base_url="http://localhost:8888", current_contest_id="abc123"))
    runner = CliRunner()

    result = runner.invoke(app, ["config", "set-url", "http://example.com"])

    assert result.exit_code == 0
    assert store.load().base_url == "http://example.com"
    assert store.load().current_contest_id == ""


def test_config_set_url_keeps_current_contest_when_url_unchanged(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HYDRO_CLI_CONFIG_DIR", str(tmp_path))
    store = ConfigStore()
    store.save(Config(base_url="http://localhost:8888", current_contest_id="abc123"))
    runner = CliRunner()

    result = runner.invoke(app, ["config", "set-url", "localhost:8888/"])

    assert result.exit_code == 0
    assert store.load().base_url == "http://localhost:8888"
    assert store.load().current_contest_id == "abc123"


def test_config_strict_submit_toggles_output_mode(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HYDRO_CLI_CONFIG_DIR", str(tmp_path))
    store = ConfigStore()
    store.save(Config(base_url="http://localhost:8888"))
    runner = CliRunner()

    result = runner.invoke(app, ["config", "strict-submit", "on"])

    assert result.exit_code == 0
    assert store.load().strict_submit

    result = runner.invoke(app, ["config", "strict-submit", "off"])

    assert result.exit_code == 0
    assert not store.load().strict_submit


def test_config_show_displays_strict_submit(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HYDRO_CLI_CONFIG_DIR", str(tmp_path))
    ConfigStore().save(Config(base_url="http://localhost:8888", strict_submit=True))
    runner = CliRunner()

    result = runner.invoke(app, ["config", "show"])

    assert result.exit_code == 0
    assert "strict_submit" in result.stdout
    assert "on" in result.stdout
