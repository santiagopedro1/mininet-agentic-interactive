from agno.tools import tool
from utils.context import get_shadow_topology, get_mininet, set_mininet, get_team, get_worker_model
from agents.switch import make_switch_agent

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.clean import cleanup

from typing import Optional

from utils.flows import remove_flow_rules
from utils.neighbors import get_switch_neighbors

@tool
def list_topology() -> dict:
    """Returns the current shadow topology as JSON."""
    topo = get_shadow_topology()
    return topo

@tool
def deploy_topology() -> str:
    """
    Applies the shadow topology to the real network. 
    This restarts Mininet and recreates all switch agents.
    """
    old_net = get_mininet()
    topo = get_shadow_topology()
    team = get_team()
    model = get_worker_model()
    
    # 1. Para e limpa a rede antiga, se existir
    if old_net:
        old_net.stop()
    cleanup()

    # 2. Cria a nova rede baseada no topo atualizado
    net = Mininet(controller=None, link=TCLink)
    set_mininet(net)
    
    # 3. Aplicar Hosts
    for h_name, h_conf in topo["hosts"].items():
        if h_conf.get("ip"):
            net.addHost(h_name, ip=h_conf["ip"])
        else:
            net.addHost(h_name)
            
    # 4. Aplicar Switches
    for s_name in topo["switches"].keys():
        net.addSwitch(s_name, failMode='standalone', stp=False, inband=False)
        remove_flow_rules(net, s_name)
        
    # 5. Aplicar Links
    for link in topo["links"]:
        n1 = net.get(link["node1"])
        n2 = net.get(link["node2"])
        net.addLink(n1, n2, **link["params"])
        
    # 6. Inicia a rede
    net.start()
    
    # 7. Refaz o time de agentes
    if team and model:
        # Deixa somente os agentes não relacionados a switches
        team.members = [m for m in team.members if "Switch" not in m.name]
        for s_name in topo["switches"].keys():
            # Faz e adiciona um agente de switch para cada switch do topo
            agent = make_switch_agent(name=s_name, neighbors=get_switch_neighbors(s_name), model=model)
            team.members.append(agent)
            
    return "Topology successfully deployed! Network restarted and fresh switch agents initialized."

@tool
def add_host(name: str, ip: Optional[str] = None) -> str:
    """Draft a host to be added to the network."""
    topo = get_shadow_topology()
    
    if name in topo["hosts"] or name in topo["switches"]:
        return f"Node {name} already exists in the shadow topology."
        
    topo["hosts"][name] = {"ip": ip} if ip else {}
    return f"Host {name} added to shadow topology. Run the deploy tool to apply changes."

@tool
def add_switch(name: str) -> str:
    """Draft a switch to be added to the network."""
    topo = get_shadow_topology()
    
    if name in topo["hosts"] or name in topo["switches"]:
        return f"Node {name} already exists in the shadow topology."
        
    topo["switches"][name] = {}
    return f"Switch {name} added to shadow topology. Run the deploy tool to apply changes."

@tool
def add_link(node1: str, node2: str, bw: Optional[float] = None, delay: Optional[str] = None, loss: Optional[int] = None) -> str:
    """Draft a link with configuration parameters."""
    topo = get_shadow_topology()
    
    # Validation
    all_nodes = list(topo["hosts"].keys()) + list(topo["switches"].keys())
    if node1 not in all_nodes or node2 not in all_nodes:
        return f"Error: One or both nodes ({node1}, {node2}) do not exist in the shadow topology."
    
    # Build config object
    params = {}
    if bw is not None: params['bw'] = bw
    if delay is not None: params['delay'] = delay
    if loss is not None: params['loss'] = loss
    
    # Prevent duplicate identical links
    for link in topo["links"]:
        if (link["node1"] == node1 and link["node2"] == node2) or (link["node1"] == node2 and link["node2"] == node1):
            return f"Link between {node1} and {node2} already exists. Remove it first to reconfigure."
            
    topo["links"].append({
        "node1": node1, 
        "node2": node2, 
        "params": params
    })
    
    return f"Link {node1}-{node2} drafted with params: {params}. Run deploy tool to apply."

@tool
def remove_node(name: str) -> str:
    """Remove a node from the shadow topology."""
    topo = get_shadow_topology()
    
    if name in topo["hosts"]:
        del topo["hosts"][name]
    elif name in topo["switches"]:
        del topo["switches"][name]
    else:
        return f"Node {name} not found in shadow topology."
        
    # Clean up any links attached to this node
    topo["links"] = [l for l in topo["links"] if l["node1"] != name and l["node2"] != name]
    
    return f"Node {name} removed from shadow topology. Run deploy to apply."

@tool
def remove_link(node1: str, node2: str) -> str:
    """Draft the removal of a link between two nodes in the shadow topology."""
    topo = get_shadow_topology()
    
    initial_link_count = len(topo["links"])
    
    # Rebuild the list, keeping only links that DO NOT connect node1 and node2.
    # We check both directions (node1->node2 and node2->node1) since links are bidirectional.
    topo["links"] = [
        link for link in topo["links"] 
        if not ((link["node1"] == node1 and link["node2"] == node2) or 
                (link["node1"] == node2 and link["node2"] == node1))
    ]
    
    # Check if we actually removed anything
    if len(topo["links"]) < initial_link_count:
        return f"Link between {node1} and {node2} removed from shadow topology. Run deploy tool to apply."
    else:
        return f"No link found between {node1} and {node2} in the shadow topology."