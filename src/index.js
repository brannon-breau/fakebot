require('dotenv').config();
const { Client, GatewayIntentBits, REST, Routes, MessageFlags } = require('discord.js');
const commands = require('../commands.json');
const { toApiCommand } = require('./lib/commandSchema');

const { DISCORD_TOKEN, DISCORD_CLIENT_ID, GUILD_ID, N8N_WEBHOOK_URL } = process.env;

if (!DISCORD_TOKEN || !DISCORD_CLIENT_ID) {
  console.error('Missing DISCORD_TOKEN or DISCORD_CLIENT_ID in environment.');
  process.exit(1);
}
if (!N8N_WEBHOOK_URL) {
  console.error('Missing N8N_WEBHOOK_URL in environment.');
  process.exit(1);
}

async function syncCommands() {
  const rest = new REST({ version: '10' }).setToken(DISCORD_TOKEN);
  const body = commands.map(toApiCommand);
  const route = GUILD_ID
    ? Routes.applicationGuildCommands(DISCORD_CLIENT_ID, GUILD_ID)
    : Routes.applicationCommands(DISCORD_CLIENT_ID);

  await rest.put(route, { body });
  console.log(
    `Synced ${body.length} command(s) ${GUILD_ID ? `to guild ${GUILD_ID}` : 'globally'}: ${body
      .map((c) => c.name)
      .join(', ')}`
  );
}

async function forwardToN8n(interaction) {
  const payload = {
    command: interaction.commandName,
    options: interaction.options.data,
    user: {
      id: interaction.user.id,
      username: interaction.user.username,
    },
    guildId: interaction.guildId,
    channelId: interaction.channelId,
    interactionId: interaction.id,
    receivedAt: new Date().toISOString(),
  };

  const res = await fetch(N8N_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`n8n webhook responded with ${res.status}`);
  }
}

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.once('ready', async () => {
  console.log(`Logged in as ${client.user.tag}`);
  try {
    await syncCommands();
  } catch (err) {
    console.error('Failed to sync slash commands:', err);
  }
});

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  try {
    await interaction.reply({ content: 'Got it ✅', flags: MessageFlags.Ephemeral });
  } catch (err) {
    console.error('Failed to ack interaction:', err);
  }

  try {
    await forwardToN8n(interaction);
  } catch (err) {
    console.error('Failed to forward interaction to n8n:', err);
  }
});

client.login(DISCORD_TOKEN);
