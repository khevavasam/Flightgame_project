from game.core.commands.command import CommandResult, CommandStatus, get_command
from game.utils.colors import err


def handle_input(game, raw: str) -> CommandResult:
    cmd = get_command(raw)
    if not cmd:
        return CommandResult([err("Invalid command, try again")], CommandStatus.ERROR)

    result = cmd.execute(game, args=raw)
    return result
