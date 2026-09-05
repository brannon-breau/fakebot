const { ApplicationCommandOptionType } = require('discord.js');

function toApiCommand(cmd) {
  return {
    name: cmd.name,
    description: cmd.description,
    options: (cmd.options || []).map((opt) => ({
      name: opt.name,
      description: opt.description,
      type: ApplicationCommandOptionType[opt.type] ?? ApplicationCommandOptionType.String,
      required: !!opt.required,
    })),
  };
}

module.exports = { toApiCommand };
