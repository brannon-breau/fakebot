# Discord Slash Bridge

Minimal Discord bot: stays online, registers slash commands, and forwards each
invocation to an n8n webhook. It does no other logic — n8n owns everything
that happens after the command fires.

## How it works

1. On startup, the bot reads `commands.json` and syncs those slash commands
   with Discord (guild-scoped if `GUILD_ID` is set, otherwise global).
2. It connects to Discord's gateway and stays online.
3. When a user runs a slash command, the bot:
   - Replies with an ephemeral "Got it ✅" (so Discord doesn't show the
     interaction as failed) — this is the only thing the user in Discord sees.
   - POSTs the command name, options, user, guild, and channel to
     `N8N_WEBHOOK_URL`.
4. n8n takes it from there. The bot does not wait for or relay n8n's response.

## Setup

1. Create an application + bot at https://discord.com/developers/applications.
   - Under **Bot**, copy the token → `DISCORD_TOKEN`.
   - Under **General Information**, copy the Application ID → `DISCORD_CLIENT_ID`.
   - Invite the bot to your server with the `bot` and `applications.commands`
     scopes (no special permissions are needed since it doesn't post messages
     to channels).
2. Copy `.env.example` to `.env` and fill in the values. Set `GUILD_ID` to your
   server ID while testing — guild commands appear instantly, global ones can
   take up to an hour.
3. In n8n, create a Webhook node (POST) and put its production URL in
   `N8N_WEBHOOK_URL`.
4. Edit `commands.json` to define whatever slash commands you want exposed.
   Option `type` values match Discord's application command option types
   (`STRING`, `INTEGER`, `BOOLEAN`, `USER`, `CHANNEL`, `ROLE`, `MENTIONABLE`,
   `NUMBER`, `ATTACHMENT`).

## Run

```
docker compose up --build -d
```

Commands are (re)synced automatically every time the bot starts, so editing
`commands.json` and restarting the container is enough to update them.

## Payload sent to n8n

```json
{
  "command": "hello",
  "options": [{ "name": "name", "type": 3, "value": "world" }],
  "user": { "id": "123", "username": "someone" },
  "guildId": "456",
  "channelId": "789",
  "interactionId": "abc",
  "receivedAt": "2026-09-04T12:00:00.000Z"
}
```
