def install_bidirectional_path(net, path):
    """Instala regras com simetria de caminho usando in_port."""

    src_host = net.get(path[0])
    dst_host = net.get(path[-1])

    for i in range(1, len(path) - 1):
        sw = net.get(path[i])
        next_node = net.get(path[i+1])
        prev_node = net.get(path[i-1])

        # Portas físicas
        out_port = sw.ports[sw.connectionsTo(next_node)[0][0]]
        in_port = sw.ports[sw.connectionsTo(prev_node)[0][0]]

        # Regras com simetria (IDA)
        forward_rule = (
            f'priority=500,in_port={in_port},ip,nw_dst={dst_host.IP()},'
            f'actions=output:{out_port}'
        )

        # Regras com simetria (VOLTA)
        reverse_rule = (
            f'priority=500,in_port={out_port},ip,nw_dst={src_host.IP()},'
            f'actions=output:{in_port}'
        )

        # ARP (necessário, mas pode ser melhorado depois)
        arp_rule = 'priority=600,arp,actions=flood'

        for cmd in [forward_rule, reverse_rule, arp_rule]:
            sw.cmd(f'ovs-ofctl add-flow {sw.name} "{cmd}"')

def remove_flow_rules(net, sw_name):
    """Remove todas as regras de fluxo de um switch específico."""
    sw = net.get(sw_name)
    sw.cmd(f'ovs-ofctl del-flows {sw.name}')