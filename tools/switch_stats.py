from agno.tools import tool
from tools.context import get_mininet
import re


def parse_tc_output(output: str):
    stats = {
        "qdisc": None,
        "sent_bytes": 0,
        "sent_packets": 0,
        "dropped": 0,
        "overlimits": 0,
        "requeues": 0,
        "backlog_bytes": 0,
        "backlog_packets": 0,
    }

    config = {
        "delay": None,
        "loss": None,
        "jitter": None,
        "rate": None,
    }

    if not output:
        return stats, config

    # qdisc type
    m = re.search(r"qdisc (\w+)", output)
    if m:
        stats["qdisc"] = m.group(1)

    # Sent / dropped
    m = re.search(
        r"Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+) requeues (\d+)\)",
        output,
    )
    if m:
        stats["sent_bytes"] = int(m.group(1))
        stats["sent_packets"] = int(m.group(2))
        stats["dropped"] = int(m.group(3))
        stats["overlimits"] = int(m.group(4))
        stats["requeues"] = int(m.group(5))

    # backlog
    m = re.search(r"backlog (\d+)b (\d+)p", output)
    if m:
        stats["backlog_bytes"] = int(m.group(1))
        stats["backlog_packets"] = int(m.group(2))

    # config extraction
    m = re.search(r"delay ([\d\.]+ms)", output)
    if m:
        config["delay"] = m.group(1)

    m = re.search(r"loss ([\d\.]+%)", output)
    if m:
        config["loss"] = m.group(1)

    m = re.search(r"delay [\d\.]+ms ([\d\.]+ms)", output)
    if m:
        config["jitter"] = m.group(1)

    m = re.search(r"rate (\S+)", output)
    if m:
        config["rate"] = m.group(1)

    return stats, config


@tool(
    name="switch_stats_tool",
    description=(
        "Get Mininet switch interface statistics. "
        "Returns per-interface traffic counters and tc (netem) statistics "
        "such as sent packets, dropped packets, delay, and loss. "
        "Does NOT include CPU, memory, or system-level metrics."
    )
)
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
        if intf.name == "lo":
            continue

        if not intf.link:
            continue

        link = intf.link
        other = link.intf1 if link.intf2 == intf else link.intf2

        # sysfs stats
        rx = sw.cmd(f"cat /sys/class/net/{intf.name}/statistics/rx_bytes").strip()
        tx = sw.cmd(f"cat /sys/class/net/{intf.name}/statistics/tx_bytes").strip()

        # tc stats
        tc_output = sw.cmd(f"tc -s qdisc show dev {intf.name}")
        tc_stats, tc_config = parse_tc_output(tc_output)

        stats["interfaces"].append({
            "interface": intf.name,
            "peer": other.node.name,
            "peer_interface": other.name,

            "sysfs": {
                "rx_bytes": int(rx) if rx.isdigit() else 0,
                "tx_bytes": int(tx) if tx.isdigit() else 0
            },

            "tc": tc_stats,
            "tc_config": tc_config
        })

    return stats