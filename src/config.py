from __future__ import annotations

import os


class Config:
    bot_token: str
    admin_ids: set[int]

    def __init__(self) -> None:
        self.bot_token = os.getenv("BOT_TOKEN", "")
        raw_admins = os.getenv("ADMIN_IDS", "")
        self.admin_ids = {
            int(part.strip())
            for part in raw_admins.split(",")
            if part.strip().isdigit()
        }

    def validate(self) -> None:
        if not self.bot_token:
            raise RuntimeError("BOT_TOKEN is required")
