import asyncio
import os
import sys

import aiohttp
from dotenv import load_dotenv

from command_schema import load_commands, to_api_command

load_dotenv()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
GUILD_ID = os.environ.get("GUILD_ID")

API_BASE = "https://discord.com/api/v10"


async def main():
    if not DISCORD_TOKEN or not DISCORD_CLIENT_ID:
        print("Missing DISCORD_TOKEN or DISCORD_CLIENT_ID in environment.", file=sys.stderr)
        sys.exit(1)

    body = [to_api_command(cmd) for cmd in load_commands()]

    if GUILD_ID:
        url = f"{API_BASE}/applications/{DISCORD_CLIENT_ID}/guilds/{GUILD_ID}/commands"
        scope = f"guild {GUILD_ID}"
    else:
        url = f"{API_BASE}/applications/{DISCORD_CLIENT_ID}/commands"
        scope = "globally (may take up to 1 hour to appear)"

    print(f"Registering {len(body)} command(s) to {scope}...")

    headers = {"Authorization": f"Bot {DISCORD_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.put(url, json=body, headers=headers) as resp:
            data = await resp.json()
            if resp.status >= 400:
                print(f"Failed ({resp.status}): {data}", file=sys.stderr)
                sys.exit(1)
            names = ", ".join(c["name"] for c in data)
            print(f"Done. Registered: {names}")


if __name__ == "__main__":
    asyncio.run(main())
