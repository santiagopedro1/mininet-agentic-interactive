from agno.tools import tool

from tools.context import get_mininet

@tool
def ping_tool(src: str, dst: str, count: int = 5) -> str:
    """
    Run ping between two hosts in Mininet.

    Args:
        src: source host
        dst: destination host
        count: number of ICMP packets to send (default 5)
    """
    net = get_mininet()

    if net is None:
        return "Mininet not initialized"

    h1 = net.get(src)
    h2 = net.get(dst)

    if h1 is None or h2 is None:
        return f"One or both hosts not found: {src}, {dst}. Double check the topology with list_topology_tool."

    result = h1.cmd(f"ping -c {count} {h2.IP()}")
    return result
