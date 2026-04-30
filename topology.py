TOPOLOGY = {
    "h1": ["s1"],
    "h2": ["s2", "s3"],
    "s1": ["h1", "s2", "s3"],
    "s2": ["s1", "h2"],
}

def topology_to_text(topo):
    seen = set()
    lines = []

    for node, neighbors in topo.items():
        for n in neighbors:
            edge = tuple(sorted([node, n]))
            if edge not in seen:
                seen.add(edge)
                lines.append(f"{edge[0]} - {edge[1]}")

    return "\n".join(lines)