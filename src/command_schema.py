import json
import os

OPTION_TYPES = {
    "SUB_COMMAND": 1,
    "SUB_COMMAND_GROUP": 2,
    "STRING": 3,
    "INTEGER": 4,
    "BOOLEAN": 5,
    "USER": 6,
    "CHANNEL": 7,
    "ROLE": 8,
    "MENTIONABLE": 9,
    "NUMBER": 10,
    "ATTACHMENT": 11,
}

COMMANDS_PATH = os.path.join(os.path.dirname(__file__), "..", "commands.json")


def load_commands():
    with open(COMMANDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def to_api_command(cmd):
    return {
        "name": cmd["name"],
        "description": cmd["description"],
        "options": [
            {
                "name": opt["name"],
                "description": opt["description"],
                "type": OPTION_TYPES.get(opt.get("type", "STRING"), OPTION_TYPES["STRING"]),
                "required": bool(opt.get("required", False)),
            }
            for opt in cmd.get("options", [])
        ],
    }
