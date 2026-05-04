from agno.tools import tool
from tools.context import get_mininet
import re


def parse_tc_output(output: str, class_output: str = ""):
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

    config: dict[str, str | None] = {
        "delay": None,
        "loss": None,
        "jitter": None,
        "bandwidth": None,
    }

    if not output:
        return stats, config

    # Extract standard stats from 'tc -s qdisc show'
    m = re.search(r"qdisc (\w+)", output)
    if m:
        stats["qdisc"] = m.group(1)

    m = re.search(r"Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+) requeues (\d+)\)", output)
    if m:
        stats["sent_bytes"] = int(m.group(1))
        stats["sent_packets"] = int(m.group(2))
        stats["dropped"] = int(m.group(3))
        stats["overlimits"] = int(m.group(4))
        stats["requeues"] = int(m.group(5))

    # Extract impairments from netem
    m = re.search(r"delay ([\d\.]+ms)", output)
    if m:
        config["delay"] = m.group(1)

    m = re.search(r"loss ([\d\.]+%)", output)
    if m:
        config["loss"] = m.group(1)

    # Extract bandwidth from 'tc class show' (HTB)
    if class_output:
        hb = re.search(r"rate (\S+)", class_output)
        if hb:
            config["bandwidth"] = hb.group(1)
    
    # Fallback: check if it was set in netem
    if not config["bandwidth"]:
        nb = re.search(r"rate (\S+)", output)
        if nb:
            config["bandwidth"] = nb.group(1)

    return stats, config


@tool(
    name="switch_interface_metrics",
    description="Fetches real-time network telemetry and traffic control (tc) configurations for a given Mininet switch. Returns structured categories: Connection, Configuration, and Telemetry."
)
def get_switch_interface_metrics(switch: str) -> dict:
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
        if intf.name == "lo" or not intf.link:
            continue

        link = intf.link
        other = link.intf1 if link.intf2 == intf else link.intf2

        # sysfs stats (Receiving)
        rx_bytes = sw.cmd(f"cat /sys/class/net/{intf.name}/statistics/rx_bytes").strip()
        rx_packets = sw.cmd(f"cat /sys/class/net/{intf.name}/statistics/rx_packets").strip()

        # tc stats (Sending/Queuing)
        tc_output = sw.cmd(f"tc -s qdisc show dev {intf.name}")
        tc_class_output = sw.cmd(f"tc class show dev {intf.name}")
        
        tc_stats, tc_config = parse_tc_output(tc_output, tc_class_output)

        # Pull qdisc type into config for better context
        qdisc_type = tc_stats.pop("qdisc")

        stats["interfaces"].append({
            "connection": {
                "local_interface": intf.name,
                "remote_node": other.node.name,
                "remote_interface": other.name
            },
            "configuration": {
                "qdisc": qdisc_type,
                **tc_config
            },
            "telemetry": {
                "rx": {
                    "bytes": int(rx_bytes) if rx_bytes.isdigit() else 0,
                    "packets": int(rx_packets) if rx_packets.isdigit() else 0
                },
                "tx": tc_stats  # Contains sent_bytes, dropped, overlimits, etc.
            }
        })

    return stats