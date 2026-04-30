MININET_NET = None

def set_mininet(net):
    global MININET_NET
    MININET_NET = net

def get_mininet():
    return MININET_NET