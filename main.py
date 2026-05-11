import readline

from mininet.log import setLogLevel

from agents.team import build_team

from utils.context import get_mininet

from rich.console import Console
from rich.markdown import Markdown

def interactive_loop(team):
    console = Console()
    while True:
        try:
            user_input = input("\nMininet-AI> ").strip()

            if user_input.lower() in {"exit", "quit"}:
                break

            if not user_input:
                continue

            result = team.run(user_input)
            console.print(Markdown(result.content))

        except KeyboardInterrupt:
            print("\nInterrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    setLogLevel('info')   # options: debug, info, warning, error

    team = build_team()

    logo = """
  __  __ _       _            _                _    ___ 
 |  \\/  (_)_ __ (_)_ __   ___| |_             / \\  |_ _|
 | |\\/| | | '_ \\| | '_ \\ / _ \\ __|  _____    / _ \\  | | 
 | |  | | | | | | | | | |  __/ |_  |_____|  / ___ \\ | | 
 |_|  |_|_|_| |_|_|_| |_|\\___|\\__|         /_/   \\_\\___|                                           
"""

    print(logo)

    interactive_loop(team)

    net = get_mininet()
    if net:
        print("\nShutting down Mininet...")
        net.stop()
