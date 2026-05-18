from agno.tools import tool

from utils.context import get_mininet

@tool
def install_flow(sw_name: str, next_name: str, dst: str) -> str:
    """Install forwarding flows on a Mininet switch.

    This tool retrieves the current Mininet network, finds the switch and
    the next-hop node, determines the output port connecting the switch to
    that next-hop, and installs both IP and ARP OpenFlow rules for the
    specified destination.

    Args:
        sw_name: Name of the switch where flows should be installed.
        next_name: Name of the next-hop node connected to the switch.
        dst: Name of the destination host for which to install the flow (used to get IP).

    Returns:
        An error message string if Mininet is not initialized, otherwise a success message.
    """
    net = get_mininet()

    if net is None:
        return "Mininet not initialized"

    sw = net.get(sw_name)
    next_node = net.get(next_name)

    out_port = sw.ports[sw.connectionsTo(next_node)[0][0]]

    dst_ip = net.get(dst).IP()

    cmds = [
        f'priority=500,ip,nw_dst={dst_ip},actions=output:{out_port}',
        f'priority=500,arp,arp_tpa={dst_ip},actions=output:{out_port}',
    ]

    for cmd in cmds:
        sw.cmd(f'ovs-ofctl add-flow {sw.name} {cmd}')

    return "Flows installed successfully"

@tool
def remove_flows(sw_name: str) -> str:
    """Remove all flows from a Mininet switch.

    This tool retrieves the current Mininet network, finds the specified switch,
    and removes all OpenFlow rules from it.

    Args:
        sw_name: Name of the switch from which to remove all flows.
    Returns:
        An error message string if Mininet is not initialized, otherwise a success message.
    """
    net = get_mininet()

    if net is None:
        return "Mininet not initialized"

    sw = net.get(sw_name)
    sw.cmd(f'ovs-ofctl del-flows {sw.name}')

    return "Flows removed successfully"