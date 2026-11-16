import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import player
from config import Settings
from models import QueueEntry, Track


class Voice:
    def __init__(self):
        self.channel = SimpleNamespace(id=10, name="Music")
        self.connected = True
        self.playing = False
        self.paused = False
        self.after = None
        self.source = None
        self.starts = asyncio.Queue()
        self.disconnect = AsyncMock(side_effect=self._disconnect)

    async def _disconnect(self, **kwargs):
        self.connected = False

    def is_connected(self):
        return self.connected

    def is_playing(self):
        return self.playing

    def is_paused(self):
        return self.paused

    def play(self, source, *, after):
        assert not self.playing and not self.paused
        self.source, self.after = source, after
        self.playing = True
        self.starts.put_nowait(source)

    def stop(self):
        if self.source:
            self.source.cleanup()
            self.source = None
        self.playing = self.paused = False
        if self.after:
            callback, self.after = self.after, None
            callback(None)

    def finish(self, error=None):
        callback, self.after = self.after, None
        self.playing = self.paused = False
        if self.source:
            self.source.cleanup()
            self.source = None
        callback(error)

    def pause(self):
        self.playing, self.paused = False, True

    def resume(self):
        self.playing, self.paused = True, False


def entry(title, channel=None):
    return QueueEntry(
        Track(title, f"https://youtu.be/{title}", f"stream:{title}"),
        channel or SimpleNamespace(send=AsyncMock()),
        SimpleNamespace(display_name="Listener", mention="@Listener"),
    )


@pytest.fixture
async def session(monkeypatch):
    async def audio(track, executable):
        return SimpleNamespace(title=track.title, cleanup=lambda: None)

    monkeypatch.setattr(player, "open_audio", audio)
    manager = player.MusicBot(SimpleNamespace(), Settings())
    session = manager.session(1)
    session.voice_client = Voice()
    yield session
    await manager.close()


@pytest.fixture
def ctx(session):
    target = SimpleNamespace(id=10, connect=AsyncMock(return_value=session.voice_client))
    return SimpleNamespace(
        guild=SimpleNamespace(id=1, voice_client=None),
        author=SimpleNamespace(voice=SimpleNamespace(channel=target), mention="@Listener"),
        channel=SimpleNamespace(send=AsyncMock()),
        send=AsyncMock(),
        prefix="!",
        command=SimpleNamespace(name="play"),
    )


async def started(session):
    return await asyncio.wait_for(session.voice_client.starts.get(), 2)
