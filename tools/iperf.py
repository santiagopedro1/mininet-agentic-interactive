from agno.tools import tool

from utils.context import get_mininet

@tool
def run_iperf_test(path: list[str], time: int) -> str:
    """Run an iperf test along a specified path in the Mininet network.

    This tool sets up OpenFlow forwarding rules along the given path for the
    destination IP, starts an iperf server on the destination host, and runs
    an iperf client on the source host for the specified duration.

    Args:
        path: List of node names defining the path, e.g., ['h1', 's1', 's2', 'h2'].
              The first element is the source host, the last is the destination host,
              and intermediate elements are switches.
        time: Duration of the iperf test in seconds.

    Returns:
        The output string from the iperf client command, or an error message.
    """
    net = get_mininet()

    if net is None:
        return "Mininet not initialized"

    if len(path) < 2:
        return "Path must have at least source and destination"

    source = path[0]
    dest = path[-1]

    try:
        dest_ip = net.get(dest).IP()
    except AttributeError:
        return f"Destination node '{dest}' not found or not a host"

    # Set up flows along the path
    for i in range(len(path) - 2):
        sw_name = path[i + 1]
        next_name = path[i + 2]

        try:
            sw = net.get(sw_name)
            next_node = net.get(next_name)
            out_port = sw.ports[sw.connectionsTo(next_node)[0][0]]
        except (KeyError, IndexError):
            return f"Failed to set up flow on switch '{sw_name}' to '{next_name}'"

        cmds = [
            f'priority=500,ip,nw_dst={dest_ip},actions=output:{out_port}',
            f'priority=500,arp,arp_tpa={dest_ip},actions=output:{out_port}'
        ]

        for cmd in cmds:
            sw.cmd(f'ovs-ofctl add-flow {sw.name} {cmd}')

    # Start iperf server on dest
    net.get(dest).cmd('iperf -s -D')

    # Run iperf client on source
    output = net.get(source).cmd(f'iperf -c {dest_ip} -t {time}')

    return output