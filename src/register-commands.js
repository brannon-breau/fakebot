require('dotenv').config();
const { REST, Routes } = require('discord.js');
const commands = require('../commands.json');
const { toApiCommand } = require('./lib/commandSchema');

const { DISCORD_TOKEN, DISCORD_CLIENT_ID, GUILD_ID } = process.env;

if (!DISCORD_TOKEN || !DISCORD_CLIENT_ID) {
  console.error('Missing DISCORD_TOKEN or DISCORD_CLIENT_ID in environment.');
  process.exit(1);
}

async function main() {
  const rest = new REST({ version: '10' }).setToken(DISCORD_TOKEN);
  const body = commands.map(toApiCommand);

  const route = GUILD_ID
    ? Routes.applicationGuildCommands(DISCORD_CLIENT_ID, GUILD_ID)
    : Routes.applicationCommands(DISCORD_CLIENT_ID);

  console.log(
    `Registering ${body.length} command(s) ${GUILD_ID ? `to guild ${GUILD_ID}` : 'globally (may take up to 1 hour to appear)'}...`
  );

  const result = await rest.put(route, { body });
  console.log(`Done. Registered: ${result.map((c) => c.name).join(', ')}`);
}

main().catch((err) => {
  console.error('Failed to register commands:', err);
  process.exit(1);
});
