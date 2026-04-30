from agno.tools import tool

from tools.context import get_mininet

@tool
def switch_stats_tool(switch: str) -> dict:

    net = get_mininet()

    if net is None:
        return {"error": "Mininet not initialized"}

    try:
        sw = net.get(switch)
    except Exception:
        return {"error": f"Switch {switch} not found"}

    stats = {
        "switch": switch,
        "interfaces": []
    }

    for intf in sw.intfList():
        # skip loopback
        if intf.name == "lo":
            continue

        # skip interfaces not connected to a link
        if not intf.link:
            continue

        link = intf.link
        other = link.intf1 if link.intf2 == intf else link.intf2

        rx = sw.cmd(f"cat /sys/class/net/{intf.name}/statistics/rx_bytes").strip()
        tx = sw.cmd(f"cat /sys/class/net/{intf.name}/statistics/tx_bytes").strip()

        stats["interfaces"].append({
            "interface": intf.name,
            "peer": other.node.name,
            "peer_interface": other.name,
            "rx_bytes": int(rx) if rx.isdigit() else 0,
            "tx_bytes": int(tx) if tx.isdigit() else 0
        })

    return stats