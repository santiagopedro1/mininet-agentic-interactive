from agno.tools import tool

from tools.context import get_mininet

@tool
def ping_tool(src: str, dst: str, count: int = 5) -> str:
    """
    Run ping between two hosts in Mininet.

    Args:
        src: source host (e.g., h1)
        dst: destination host (e.g., h2)
        count: number of ICMP packets to send (default 5)
    """
    net = get_mininet()

    if net is None:
        return "Mininet not initialized"

    h1 = net.get(src)
    h2 = net.get(dst)

    result = h1.cmd(f"ping -c {count} {h2.IP()}")
    return result