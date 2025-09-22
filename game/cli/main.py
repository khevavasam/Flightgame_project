from game.core.game import Game


def main():
    game = Game()

    while game.is_running():
        command = input("Enter airport name: ")
        if command == "exit":
            game.exit_game()
            break
        result = game.get_airport_by_name(command)
        print(result)
