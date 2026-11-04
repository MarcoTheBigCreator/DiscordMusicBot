import asyncio
import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock

import discord
import pytest

import main
from config import Settings, validate_prefix
from constants import MESSAGES
from prefixes import Prefixes
from tests.conftest import entry
from views import HelpPaginator, QueuePaginator, fit_embed


def test_import_has_no_dotenv_or_discord_login(monkeypatch):
    import dotenv

    def forbidden(*args, **kwargs):
        raise AssertionError("import read configuration")

    monkeypatch.setattr(dotenv, "load_dotenv", forbidden)
    monkeypatch.setattr(discord.Client, "start", forbidden)
    importlib.reload(main)
    assert "token" not in repr(Settings(token="sensitive"))
    assert "sensitive" not in repr(Settings(token="sensitive"))


def test_bot_help_never_loads_credentials(monkeypatch, capsys):
    import sys

    monkeypatch.setattr(sys, "argv", ["bot", "--help"])

    def forbidden():
        raise AssertionError("help loaded credentials")

    monkeypatch.setattr(main.Settings, "load", forbidden)
    with pytest.raises(SystemExit) as result:
        main.run()
    assert result.value.code == 0
    assert "Crummy Discord music bot" in capsys.readouterr().out


@pytest.mark.parametrize("prefix", ["", "a b", "a" * 11, "a\n"])
def test_invalid_prefix(prefix):
    with pytest.raises(ValueError):
        validate_prefix(prefix)


async def test_atomic_prefix_per_guild_and_failed_write(tmp_path, monkeypatch):
    path = tmp_path / "prefixes.json"
    store = Prefixes(path, "-")
    await asyncio.gather(store.set(1, "!"), store.set(2, "?"))
    again = Prefixes(path, "-")
    assert (again.get(1), again.get(2), again.get(3)) == ("!", "?", "-")

    def fail(*args):
        raise OSError("disk full")

    monkeypatch.setattr(store, "_write", fail)
    with pytest.raises(OSError):
        await store.set(1, "#")
    assert store.get(1) == "!"


async def test_help_preserves_personality_and_uses_actual_prefix():
    view = HelpPaginator(None, "!")
    assert [child.label for child in view.children] == [
        "🏠",
        "🎵",
        "📋",
        "🔄",
        "📊",
        "⚙️",
        "❌ Close",
    ]
    assert "❤️" in view.get_help_embed().footer.text
    view.current_category = "music"
    assert any("!play" in field.value for field in view.get_help_embed().fields)
    assert all("`-" not in field.value for field in view.get_help_embed().fields)


async def test_queue_clamps_after_shrink_and_timeout_edits_message(session):
    session.pending = [entry(str(i)) for i in range(25)]
    view = QueuePaginator(session, 100)
    assert view.current_page == 3
    session.pending = session.pending[:1]
    embed = view.get_queue_embed()
    assert view.current_page == 1
    assert "1/1" in embed.title
    view.message = SimpleNamespace(edit=AsyncMock())
    await view.on_timeout()
    assert all(child.disabled for child in view.children)
    view.message.edit.assert_awaited_once_with(view=view)


async def test_public_commands_case_insensitive_aliases_and_intents(tmp_path):
    bot = main.create_bot(Settings(data_dir=tmp_path))
    try:
        await bot.setup_hook()
        for alias, name in [
            ("P", "play"),
            ("PLAY", "play"),
            ("UNPAUSE", "resume"),
            ("PRE", "prefix"),
            ("SH", "shuffle"),
            ("NP", "nowplaying"),
        ]:
            assert bot.get_command(alias).name == name
        assert bot.intents.message_content
        assert bot.intents.voice_states
        assert not bot.intents.members and not bot.intents.presences
        assert len(bot.get_command("prefix").checks) == 2
    finally:
        await bot.close()


async def test_settings_missing_token_without_reading_real_env(monkeypatch):
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args: None)
    monkeypatch.delenv("DISCORD_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="DISCORD_API_TOKEN"):
        Settings.load()


def test_original_messages_kept():
    assert MESSAGES["paused"] == "Paused"
    assert MESSAGES["loop_song"] == "🔂 Loop mode: **Song** - Current song will repeat"
    assert MESSAGES["song_removed_format"] == "Removed {}"


def configured_environment(monkeypatch):
    import dotenv

    import config

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args: None)
    monkeypatch.setattr(config.shutil, "which", lambda executable: executable)
    monkeypatch.setenv("DISCORD_API_TOKEN", "test-placeholder")
    monkeypatch.setenv("DISCORD_BOT_PREFIX", "-")
    monkeypatch.setenv("YTDLP_COOKIES_FILE", "")
    for name in (
        "WORKERS",
        "AUDIO_WORKERS",
        "REQUESTS",
        "GUILD_REQUESTS",
        "PLAYLIST_LIMIT",
        "QUEUE_LIMIT",
        "EXTRACT_TIMEOUT",
        "CONNECT_TIMEOUT",
        "STREAM_MAX_AGE",
        "CRUMMY_CONNECT_TIMEOUT",
        "MESSAGE_TTL_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)
    for name in (
        "EXTRACT_WORKERS",
        "AUDIO_WORKERS",
        "PENDING_GLOBAL",
        "PENDING_GUILD",
        "PLAYLIST_LIMIT",
        "QUEUE_LIMIT",
        "EXTRACTION_TIMEOUT",
        "STREAM_MAX_AGE",
    ):
        monkeypatch.delenv("CRUMMY_" + name, raising=False)


def test_concurrency_environment_settings_are_loaded(monkeypatch):
    configured_environment(monkeypatch)
    values = {
        "EXTRACT_WORKERS": "4",
        "AUDIO_WORKERS": "3",
        "PENDING_GLOBAL": "20",
        "PENDING_GUILD": "5",
        "PLAYLIST_LIMIT": "30",
        "QUEUE_LIMIT": "100",
        "EXTRACTION_TIMEOUT": "45.5",
        "STREAM_MAX_AGE": "60",
    }
    for name, value in values.items():
        monkeypatch.setenv("CRUMMY_" + name, value)
    settings = Settings.load()
    assert (settings.workers, settings.audio_workers) == (4, 3)
    assert (settings.pending_global, settings.pending_guild) == (20, 5)
    assert (settings.playlist_limit, settings.queue_limit) == (30, 100)
    assert (settings.extraction_timeout, settings.stream_max_age) == (45.5, 60)
    from player import MusicBot

    manager = MusicBot(None, settings)
    assert manager.media.capacity._value == 4
    assert manager.audio_capacity._value == 3


@pytest.mark.parametrize(
    "variable,value",
    [
        ("CRUMMY_EXTRACT_WORKERS", "0"),
        ("CRUMMY_EXTRACT_WORKERS", "1.5"),
        ("CRUMMY_AUDIO_WORKERS", "-1"),
        ("CRUMMY_PENDING_GLOBAL", "bad-value"),
        ("CRUMMY_EXTRACTION_TIMEOUT", "nan"),
        ("CRUMMY_STREAM_MAX_AGE", "inf"),
    ],
)
def test_invalid_environment_limits_are_rejected(monkeypatch, variable, value):
    configured_environment(monkeypatch)
    monkeypatch.setenv(variable, value)
    with pytest.raises(ValueError):
        Settings.load()


def test_environment_limits_are_optional(monkeypatch):
    configured_environment(monkeypatch)
    settings = Settings.load()
    assert (
        settings.workers,
        settings.audio_workers,
        settings.pending_global,
        settings.pending_guild,
    ) == (3, 2, 12, 3)


@pytest.mark.parametrize("value,expected", [("", None), ("0", None), ("120", 120.0), ("0.5", 0.5)])
def test_optional_message_duration(monkeypatch, value, expected):
    configured_environment(monkeypatch)
    monkeypatch.setenv("MESSAGE_TTL_SECONDS", value)
    assert Settings.load().message_ttl == expected


@pytest.mark.parametrize("value", ["-1", "nan", "inf", "not-a-number"])
def test_invalid_message_duration(monkeypatch, value):
    configured_environment(monkeypatch)
    monkeypatch.setenv("MESSAGE_TTL_SECONDS", value)
    with pytest.raises(ValueError, match="MESSAGE_TTL_SECONDS"):
        Settings.load()


def test_cookie_mode_reports_missing_solver_before_network(monkeypatch, tmp_path):
    configured_environment(monkeypatch)
    import config

    path = tmp_path / "test.cookies.txt"
    path.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    monkeypatch.setenv("YTDLP_COOKIES_FILE", str(path))

    def missing(name):
        raise config.PackageNotFoundError(name)

    monkeypatch.setattr(config, "version", missing)
    with pytest.raises(ValueError, match="uv sync --locked"):
        Settings.load()


def test_cookie_mode_reports_missing_deno_before_network(monkeypatch, tmp_path):
    configured_environment(monkeypatch)
    import config

    path = tmp_path / "test.cookies.txt"
    path.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    monkeypatch.setenv("YTDLP_COOKIES_FILE", str(path))
    monkeypatch.setattr(
        config.shutil, "which", lambda executable: None if executable == "deno" else executable
    )
    with pytest.raises(ValueError, match="Deno was not found"):
        Settings.load()


def test_established_variable_names_and_precedence(monkeypatch):
    configured_environment(monkeypatch)
    values = {
        "WORKERS": "3",
        "REQUESTS": "12",
        "GUILD_REQUESTS": "3",
        "PLAYLIST_LIMIT": "50",
        "QUEUE_LIMIT": "200",
        "EXTRACT_TIMEOUT": "60",
        "CONNECT_TIMEOUT": "30",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("CRUMMY_EXTRACT_WORKERS", "9")
    settings = Settings.load()
    assert (
        settings.workers,
        settings.pending_global,
        settings.pending_guild,
        settings.playlist_limit,
        settings.queue_limit,
        settings.extraction_timeout,
        settings.connect_timeout,
    ) == (3, 12, 3, 50, 200, 60, 30)


@pytest.mark.parametrize("value", ["0", "-1", "nan", "invalid"])
def test_connection_timeout_is_validated(monkeypatch, value):
    configured_environment(monkeypatch)
    monkeypatch.setenv("CONNECT_TIMEOUT", value)
    with pytest.raises(ValueError):
        Settings.load()


def test_embed_limits_for_long_customizations():
    embed = discord.Embed(title="a" * 400, description="b" * 5000)
    for _ in range(30):
        embed.add_field(name="c" * 300, value="d" * 2000)
    result = fit_embed(embed)
    assert len(result) <= 6000
    assert len(result.title) <= 256
    assert len(result.description) <= 4096
    assert len(result.fields) <= 25
    assert all(
        0 < len(field.name) <= 256 and 0 < len(field.value) <= 1024 for field in result.fields
    )
