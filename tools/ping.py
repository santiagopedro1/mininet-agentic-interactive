from agno.tools import tool

from utils.context import get_mininet
from utils.flows import install_bidirectional_path, remove_flow_rules

@tool
def ping(path: list[str], count: int = 5) -> str:
    """
    Run ping between two hosts in Mininet.

    Args:
        path: list of node names representing the path from source to destination (e.g., ["h1", "s1", "s2", "h2"])
        count: number of ICMP packets to send (default 5)
    """
    net = get_mininet()

    if net is None:
        return "Mininet not initialized"

    src = path[0]
    dst = path[-1]

    h1 = net.get(src)
    h2 = net.get(dst)

    if h1 is None or h2 is None:
        return f"One or both hosts not found: {src}, {dst}. Double check the topology with list_topology."

    install_bidirectional_path(net, path)

    result = h1.cmd(f"ping -c {count} {h2.IP()}")

    for sw_name in path[1:-1]:
        remove_flow_rules(net, sw_name)

    return result
