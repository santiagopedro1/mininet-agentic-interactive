_STATE = {
    "mininet": None,
    "team": None,
    "worker_model": None,
    "shadow_topology": {
        "hosts": {},       # Format: {"h1": {"ip": "10.0.0.1"}, "h2": {}}
        "switches": {},    # Format: {"s1": {}}
        "links": []        # Format: [{"node1": "h1", "node2": "s1", "params": {"bw": 10}}]
    }
}

def set_mininet(net):
    _STATE["mininet"] = net

def get_mininet():
    return _STATE["mininet"]

def set_team(team):
    _STATE["team"] = team

def get_team():
    return _STATE["team"]

def set_worker_model(model):
    _STATE["worker_model"] = model

def get_worker_model():
    return _STATE["worker_model"]

def get_shadow_topology():
    return _STATE["shadow_topology"]