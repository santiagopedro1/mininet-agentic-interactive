import readline

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Controller
from mininet.link import TCLink

from mininet.log import setLogLevel

from team import build_team

from tools.context import set_mininet

from rich.console import Console
from rich.markdown import Markdown

class SimpleTopo(Topo):
    def build(self):
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")

        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")
        s3 = self.addSwitch("s3")

        # low-latency path
        self.addLink(h1, s1, delay="1ms", loss=10, bw=5)
        self.addLink(s1, s2, delay="1ms", loss=10, bw=10)
        self.addLink(s2, h2, delay="1ms", loss=10, bw=15)

        # high-latency alternative path
        self.addLink(s1, s3, delay="10ms", loss=10)
        self.addLink(s3, h2, delay="10ms", loss=10)


def start_mininet():
    topo = SimpleTopo()
    net = Mininet(topo=topo, controller=Controller, link=TCLink)
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