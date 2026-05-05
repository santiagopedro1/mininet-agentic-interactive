import readline

from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink

from mininet.log import setLogLevel

from team import build_team

from tools.context import set_mininet

from rich.console import Console
from rich.markdown import Markdown

def start_mininet():
    # Start with an empty network
    net = Mininet(controller=Controller, link=TCLink)
    net.start()
    return net


def interactive_loop(team):
    console = Console()
    while True:
        try:
            user_input = input("\n> ").strip()

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
    net = start_mininet()
    set_mininet(net)

    team = build_team()

    interactive_loop(team)

    print("\nShutting down Mininet...")
    net.stop()
