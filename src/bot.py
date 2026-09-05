import os
import sys
from datetime import datetime, timezone

import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = os.environ.get("GUILD_ID")
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")

if not DISCORD_TOKEN:
    print("Missing DISCORD_TOKEN in environment.", file=sys.stderr)
    sys.exit(1)
if not N8N_WEBHOOK_URL:
    print("Missing N8N_WEBHOOK_URL in environment.", file=sys.stderr)
    sys.exit(1)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def notify_n8n(interaction: discord.Interaction, command: str, options: dict):
    payload = {
        "command": command,
        "options": options,
        "user": {
            "id": str(interaction.user.id),
            "username": interaction.user.name,
        },
        "guildId": str(interaction.guild_id) if interaction.guild_id else None,
        "channelId": str(interaction.channel_id) if interaction.channel_id else None,
        "interactionId": str(interaction.id),
        "receivedAt": datetime.now(timezone.utc).isoformat(),
    }

    try:
        await interaction.response.send_message("Got it ✅", ephemeral=True)
    except discord.HTTPException as err:
        print(f"Failed to ack interaction: {err}", file=sys.stderr)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(N8N_WEBHOOK_URL, json=payload) as resp:
                if resp.status >= 400:
                    raise RuntimeError(f"n8n webhook responded with {resp.status}")
    except Exception as err:
        print(f"Failed to forward interaction to n8n: {err}", file=sys.stderr)


# --- Slash commands ---------------------------------------------------------
# Add new commands here. Each one should just ack + hand off to n8n; no other
# logic belongs in this bot.


@tree.command(name="ping", description="Check that the bot is alive")
async def ping(interaction: discord.Interaction):
    await notify_n8n(interaction, "ping", {})


@tree.command(name="hello", description="Send a greeting request to n8n")
@app_commands.describe(name="Who to greet")
async def hello(interaction: discord.Interaction, name: str = ""):
    await notify_n8n(interaction, "hello", {"name": name})


# -----------------------------------------------------------------------------


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    if GUILD_ID:
        guild = discord.Object(id=int(GUILD_ID))
        tree.copy_global_to(guild=guild)
        synced = await tree.sync(guild=guild)
        print(f"Synced {len(synced)} command(s) to guild {GUILD_ID}: {', '.join(c.name for c in synced)}")
    else:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s) globally: {', '.join(c.name for c in synced)}")


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
