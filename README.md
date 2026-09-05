# Discord Slash Bridge

Minimal Discord bot: stays online, exposes a handful of slash commands, and
forwards each invocation to an n8n webhook. It does no other logic — n8n owns
everything that happens after the command fires.

## How it works

1. On startup, the bot registers its slash commands with Discord (guild-scoped
   if `GUILD_ID` is set, otherwise global) and connects to the gateway.
2. When a user runs a slash command, the bot:
   - Replies with an ephemeral "Got it ✅" (so Discord doesn't show the
     interaction as failed) — this is the only thing the user in Discord sees.
   - POSTs the command name, options, user, guild, and channel to
     `N8N_WEBHOOK_URL`.
3. n8n takes it from there. The bot does not wait for or relay n8n's response.

## Adding / changing commands

Commands are plain Python in [bot.py](bot.py) — no config file. Add a
new one with the `@tree.command(...)` decorator and call `notify_n8n`:

```python
@tree.command(name="ping", description="Check that the bot is alive")
async def ping(interaction: discord.Interaction):
    await notify_n8n(interaction, "ping", {})
```

For commands with arguments, add typed parameters and pass them through as
the `options` dict:

```python
@tree.command(name="hello", description="Send a greeting request to n8n")
@app_commands.describe(name="Who to greet")
async def hello(interaction: discord.Interaction, name: str = ""):
    await notify_n8n(interaction, "hello", {"name": name})
```

Commands are re-synced with Discord automatically every time the bot starts.

## Setup

1. Create an application + bot at https://discord.com/developers/applications.
   - Under **Bot**, copy the token → `DISCORD_TOKEN`.
   - Invite the bot to your server with the `bot` and `applications.commands`
     scopes (no special permissions are needed since it doesn't post messages
     to channels).
   - Under **Bot**, disable Privileged Gateway Intents (none are needed).
2. Copy `.env.example` to `.env` and fill in the values. Set `GUILD_ID` to your
   server ID while testing — guild commands appear instantly, global ones can
   take up to an hour.
3. In n8n, create a Webhook node (POST) and put its production URL in
   `N8N_WEBHOOK_URL`.

## Run

This runs inside the existing `python-runner` container rather than its own
Docker image:

1. Copy this folder onto the host under `python-runner`'s appdata directory,
   e.g. `/mnt/user/appdata/python-runner/discord-slash-bridge/`.
2. Bind-mount that folder to `/scripts` in the container and set the
   `SCRIPT_PATH` env var to `/scripts/bot.py`.
3. Set `DISCORD_TOKEN`, `GUILD_ID` (optional), and `N8N_WEBHOOK_URL` as env
   vars on the container itself (or via a `.env` file dropped in this same
   folder — `bot.py` loads one if present).
4. `requirements.txt` is picked up and installed automatically by the runner
   on startup.

## Payload sent to n8n

```json
{
  "command": "hello",
  "options": { "name": "world" },
  "user": { "id": "123", "username": "someone" },
  "guildId": "456",
  "channelId": "789",
  "interactionId": "abc",
  "receivedAt": "2026-09-04T12:00:00.000Z"
}
```
