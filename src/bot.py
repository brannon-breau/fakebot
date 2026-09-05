import os
import sys
from datetime import datetime, timezone

import aiohttp
import discord
from dotenv import load_dotenv

from command_schema import load_commands, to_api_command

load_dotenv()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
GUILD_ID = os.environ.get("GUILD_ID")
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")

if not DISCORD_TOKEN or not DISCORD_CLIENT_ID:
    print("Missing DISCORD_TOKEN or DISCORD_CLIENT_ID in environment.", file=sys.stderr)
    sys.exit(1)
if not N8N_WEBHOOK_URL:
    print("Missing N8N_WEBHOOK_URL in environment.", file=sys.stderr)
    sys.exit(1)

API_BASE = "https://discord.com/api/v10"

intents = discord.Intents.default()
client = discord.Client(intents=intents)


async def sync_commands(session: aiohttp.ClientSession):
    body = [to_api_command(cmd) for cmd in load_commands()]

    if GUILD_ID:
        url = f"{API_BASE}/applications/{DISCORD_CLIENT_ID}/guilds/{GUILD_ID}/commands"
        scope = f"guild {GUILD_ID}"
    else:
        url = f"{API_BASE}/applications/{DISCORD_CLIENT_ID}/commands"
        scope = "globally"

    headers = {"Authorization": f"Bot {DISCORD_TOKEN}"}
    async with session.put(url, json=body, headers=headers) as resp:
        data = await resp.json()
        if resp.status >= 400:
            print(f"Failed to sync commands ({resp.status}): {data}", file=sys.stderr)
            return
        names = ", ".join(c["name"] for c in data)
        print(f"Synced {len(data)} command(s) to {scope}: {names}")


async def forward_to_n8n(session: aiohttp.ClientSession, interaction: discord.Interaction):
    data = interaction.data or {}
    payload = {
        "command": data.get("name"),
        "options": data.get("options", []),
        "user": {
            "id": str(interaction.user.id),
            "username": interaction.user.name,
        },
        "guildId": str(interaction.guild_id) if interaction.guild_id else None,
        "channelId": str(interaction.channel_id) if interaction.channel_id else None,
        "interactionId": str(interaction.id),
        "receivedAt": datetime.now(timezone.utc).isoformat(),
    }

    async with session.post(N8N_WEBHOOK_URL, json=payload) as resp:
        if resp.status >= 400:
            raise RuntimeError(f"n8n webhook responded with {resp.status}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    async with aiohttp.ClientSession() as session:
        await sync_commands(session)


@client.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.application_command:
        return

    try:
        await interaction.response.send_message("Got it ✅", ephemeral=True)
    except discord.HTTPException as err:
        print(f"Failed to ack interaction: {err}", file=sys.stderr)

    try:
        async with aiohttp.ClientSession() as session:
            await forward_to_n8n(session, interaction)
    except Exception as err:
        print(f"Failed to forward interaction to n8n: {err}", file=sys.stderr)


client.run(DISCORD_TOKEN)
