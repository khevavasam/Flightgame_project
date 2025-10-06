"""
core/commands/command.py
========================
Implements the notorius game programming command pattern.

Defines the abstract Command interface and concrete game commands.
(Fly, Map, QuestLog, Refresh, Exit).
Includes a registry of commands and utilities for matching user input and executing commands.
"""

from abc import ABC, abstractmethod
from .result import CommandResult, CommandStatus
from game.cli.renderer import Renderer
from game.utils.colors import info, warn, err, bold, dim
from typing import Optional


class Command(ABC):
    """Abstract base class for game commands."""

    name: str

    aliases: tuple[str, ...] = ()

    def matches(self, text: str) -> bool:
        """Check if `text` matches the command name or any aliases."""
        return text == self.name.lower() or text in [a.lower() for a in self.aliases]

    @abstractmethod
    def execute(self, game, args: str = "") -> CommandResult:
        """
        Execute the game command.

        Args:
            game (Game): The game instance.
            args (str): Optional arguments (e.g. 1,2,3..)
        Returns:
            CommandResult: Result including messages and result status (ok | error).
        """
        ...


COMMANDS: dict[str, type[Command]] = {}


def get_command(input_text: str) -> Optional[Command]:
    """
    Get a Command object matching the `input_text`.

    Args:
        input_text (str): User input text.

    Returns:
        Optional[Command]: Matched Command instance or None.
    """
    input_text = input_text.strip().lower()
    cmd_cls = COMMANDS.get(input_text)
    if cmd_cls:
        return cmd_cls()
    for cls in set(COMMANDS.values()):
        cmd = cls()
        if hasattr(cmd, "matches") and cmd.matches(input_text):
            return cmd
    return None


def register_command(cls: type[Command]):
    """Decorator to register a Command class in the COMMAND registry."""
    COMMANDS[cls.name.lower()] = cls
    for alias in cls.aliases:
        COMMANDS[alias.lower()] = cls
    return cls


@register_command
class FlyCommand(Command):
    """Command to fly to a chosen airport."""

    name = "fly"

    def matches(self, text: str) -> bool:
        """Match digits as valid input."""
        return text.isdigit()

    def execute(self, game, args="") -> CommandResult:
        """Execute flying to the chosen airport."""
        if not args.isdigit():
            return CommandResult(
                [err("You must enter the number of a destination.")],
                CommandStatus.ERROR,
            )
        idx = int(args)
        opts = game.options()
        if not (1 <= idx <= len(opts)):
            return CommandResult(
                [err(f"Invalid option number. {idx}")], CommandStatus.ERROR
            )

        chosen = game.pick(idx)
        if not chosen:
            return CommandResult(
                [err(f"Unable to fly to destination: {chosen}")], CommandStatus.ERROR
            )

        messages: list[str] = [
            info(f"\n>>> Flying to {chosen.name} ({chosen.icao}) >>>")
        ]
        # Include event messages triggered by game.pick()
        for msg in game._event_messages:
            messages.append(msg)
        game._event_messages.clear()

        if game.state.system_msg:
            messages.append(warn(game.state.system_msg))
            game.state.system_msg = ""

        return CommandResult(messages, CommandStatus.OK)


@register_command
class MapCommand(Command):
    """Command to view the map."""

    name = "map"
    aliases = ("m",)

    def execute(self, game, args="") -> CommandResult:
        """Render the map including airports, target and player."""
        r = Renderer()

        current = game.state.player.location
        target = game.get_target_airport()
        airports = game.get_airports()

        legend = f"{dim('*')} airports {bold(info('@'))} you {bold(err('X'))} target "
        raw_map = r.draw_map(current, target, airports)
        palette = {"*": dim("*"), "@": bold(info("@")), "X": bold(err("X"))}
        coloured = "".join(palette.get(ch, ch) for ch in raw_map)
        return CommandResult([legend, coloured], CommandStatus.OK)


@register_command
class QuestLogCommand(Command):
    """Command to view the quest log."""

    name = "quests"
    aliases = ("quest", "questlog")

    def execute(self, game, args="") -> CommandResult:
        """Display the quest log including active and completed quests (visual only)."""
        if not game.state:
            return CommandResult([err("Game not started.")], CommandStatus.ERROR)

        messages: list[str] = []
        messages.append(bold("Quest Log"))
        messages.append(dim("—" * 32))

        # Active
        messages.append(info("Active:"))
        active_quest = game.state.active_quest
        if active_quest:
            rem = game.remaining_distance_to_target()
            rem_txt = f"{rem} km remaining" if rem is not None else "distance unknown"
            messages.append(f"  -> Fly to {bold(active_quest.target_icao)} {dim(f'({rem_txt})')}")
        else:
            messages.append(dim("  -> None"))

        # Completed
        messages.append("")
        completed_quests = game.state.completed_quests
        if completed_quests:
            messages.append(ok("Completed:"))
            for i, q in enumerate(completed_quests, start=1):
                messages.append(dim(f"  {i}. ") + bold(f"{q.target_icao}"))
        else:
            messages.append(dim("Completed:\n  - None"))

        messages.append("")
        messages.append(bold(f"Total points: {game.state.points}"))
        messages.append(dim("—" * 32))

        return CommandResult(messages, CommandStatus.OK)


@register_command
class RefreshCommand(Command):
    """Command to refresh the game status."""

    name = "refresh"
    aliases = ("r", "i")

    def execute(self, game, args="") -> CommandResult:
        """Refresh the game status."""
        if not game.state:
            return CommandResult([err("Game not started.")], CommandStatus.ERROR)
        return CommandResult(["Refreshing..."], CommandStatus.OK)


@register_command
class ExitCommand(Command):
    name = "exit"
    aliases = ("q", "quit")

    def execute(self, game, args="") -> CommandResult:
        game.exit_game()
        return CommandResult([info("Goodbye - game ended.")], CommandStatus.OK)
