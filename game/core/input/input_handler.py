"""
core/input/inputhandler.py
==========================
Handles parsing and executing user input commands.

Provides `handle_input` to convert raw user input into a CommandResult.
"""

from game.core.commands.command import CommandResult, CommandStatus, get_command
from game.utils.colors import err


def handle_input(game, raw: str) -> CommandResult:
    """
    Parse and execute a raw input string as a game command.

    Args:
        game (Game): The game instance.
        raw (str): Raw user input string.

    Returns:
        CommandResult: Result containing messages produced by the command and execution status.
    """
    cmd = get_command(raw)
    if not cmd:
        return CommandResult([err("Invalid command, try again")], CommandStatus.ERROR)

    result = cmd.execute(game, args=raw)
    return result
