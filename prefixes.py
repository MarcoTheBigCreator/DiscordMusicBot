"""One-process, per-guild persistence; never rewrites .env."""

import asyncio
import json
import os
from pathlib import Path

from config import validate_prefix


class Prefixes:
    def __init__(self, path: Path, default: str):
        self.path, self.default = path, default
        self.lock = asyncio.Lock()
        self.values = {}
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Invalid prefixes.json: expected an object.")
            for guild, prefix in data.items():
                if not guild.isdecimal() or not isinstance(prefix, str):
                    raise ValueError("Invalid prefixes.json entry.")
                validate_prefix(prefix)
            self.values = data

    def get(self, guild_id):
        return self.values.get(str(guild_id), self.default)

    async def set(self, guild_id, prefix):
        validate_prefix(prefix)
        async with self.lock:
            updated = {**self.values, str(guild_id): prefix}
            write = asyncio.create_task(asyncio.to_thread(self._write, updated))
            try:
                await asyncio.shield(write)
            except asyncio.CancelledError:
                await write
                self.values = updated
                raise
            self.values = updated

    def _write(self, updated):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        try:
            with temporary.open("w", encoding="utf-8") as handle:
                json.dump(updated, handle, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)
