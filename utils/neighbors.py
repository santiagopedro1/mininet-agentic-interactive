from utils.context import get_mininet

def get_switch_neighbors(switch_name: str):
    net = get_mininet()
    if net is None:
        return []

    try:
        sw = net.get(switch_name)
    except Exception:
        return []

    neighbors = []

    for intf in sw.intfList():
        link = intf.link
        if not link:
            continue

        # get the other side of the link
        other_intf = link.intf1 if link.intf2 == intf else link.intf2
        node = other_intf.node

        if node.name != switch_name:
            neighbors.append(node.name)

    return neighbors