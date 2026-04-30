import readline

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Controller
from mininet.link import TCLink

from mininet.log import setLogLevel

from team import build_team

from tools.context import set_mininet

class SimpleTopo(Topo):
    def build(self):
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")

        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")
        s3 = self.addSwitch("s3")

        # low-latency path
        self.addLink(h1, s1, delay="1ms")
        self.addLink(s1, s2, delay="1ms")
        self.addLink(s2, h2, delay="1ms")

        # high-latency alternative path
        self.addLink(s1, s3, delay="10ms")
        self.addLink(s3, h2, delay="10ms")


def start_mininet():
    topo = SimpleTopo()
    net = Mininet(topo=topo, controller=Controller, link=TCLink)
    net.start()
    return net


def print_disclaimer():
    print("=" * 60)
    print("Mininet LLM Control Interface")
    print("=" * 60)
    print("""
This tool allows you to interact with a simulated network using natural language.

Capabilities:
- Compute paths between hosts (uses deterministic routing)
- Test connectivity using ping (real Mininet execution)
- Query basic network structure

Limitations:
- No persistent state or learning
- Limited understanding of complex policies
- May require clear, explicit queries

Examples:
- "Find path from h1 to h2"
- "Ping from h1 to h2"

Type 'exit' or 'quit' to stop.
""")
    print("=" * 60)


def interactive_loop(team):
    while True:
        try:
            user_input = input("\n> ").strip()

            if user_input.lower() in {"exit", "quit"}:
                break

            if not user_input:
                continue

            result = team.run(user_input)
            # print(result.content)

        except KeyboardInterrupt:
            print("\nInterrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    setLogLevel('info')   # options: debug, info, warning, error
    net = start_mininet()
    set_mininet(net)

    team = build_team()

    print_disclaimer()
    interactive_loop(team)

    print("\nShutting down Mininet...")
    net.stop()