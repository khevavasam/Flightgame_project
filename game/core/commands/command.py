from abc import ABC, abstractmethod
from .result import CommandResult, CommandStatus
from game.cli.renderer import Renderer
from game.utils.colors import info, warn, err, bold, dim
from typing import Optional


class Command(ABC):
    name: str

    aliases: tuple[str, ...] = ()

    def matches(self, text: str) -> bool:
        return text == self.name.lower() or text in [a.lower() for a in self.aliases]

    @abstractmethod
    def execute(self, game, args: str = "") -> CommandResult: ...


COMMANDS: dict[str, type[Command]] = {}


def get_command(input_text: str) -> Optional[Command]:
    input_text = input_text.strip().lower()
    cmd_cls = COMMANDS.get(input_text)
    if cmd_cls:
        return cmd_cls()
    for cls in set(COMMANDS.values()):
        cmd = cls()
        if hasattr(cmd, "matches") and cmd.matches(input_text):
            return cmd
    return None


# Decorator.
def register_command(cls: type[Command]):
    COMMANDS[cls.name.lower()] = cls
    for alias in cls.aliases:
        COMMANDS[alias.lower()] = cls
    return cls


@register_command
class FlyCommand(Command):
    name = "fly"

    def matches(self, text: str) -> bool:
        return text.isdigit()

    def execute(self, game, args="") -> CommandResult:
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
    name = "map"
    aliases = ("m",)

    def execute(self, game, args="") -> CommandResult:
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
    name = "quests"
    aliases = ("quest", "questlog")

    def execute(self, game, args="") -> CommandResult:
        if not game.state:
            return CommandResult([err("Game not started.")], CommandStatus.ERROR)
        messages = [bold("Quest Log")]
        active_quest = game.state.active_quest
        if active_quest:
            rem = game.remaining_distance_to_target()
            messages.append(
                f"Active:\n Fly to {active_quest.target_icao} - {rem} km remaining"
            )
        else:
            messages.append("Active:\n- None")

        completed_quests = game.state.completed_quests
        if completed_quests:
            messages.append("\nCompleted:")
            for i, q in enumerate(completed_quests, start=1):
                messages.append(f"{i} {q.target_icao}")
        else:
            messages.append("\nCompleted:\n- None")

        messages.append(bold(f"\nTotal points: {game.state.points}"))
        return CommandResult(messages, CommandStatus.OK)


@register_command
class RefreshCommand(Command):
    name = "refresh"
    aliases = ("r", "i")

    def execute(self, game, args="") -> CommandResult:
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
