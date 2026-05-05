from agno.tools import tool
from context import get_shadow_topology, get_mininet, set_mininet, get_team, get_worker_model
from agents.switch import make_switch_agent

from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.clean import cleanup

from typing import Optional

@tool
def list_topology_tool() -> dict:
    """Returns the current shadow topology as JSON."""
    topo = get_shadow_topology()
    return topo

@tool
def deploy_topology_tool() -> str:
    """
    Applies the shadow topology to the real network. 
    This restarts Mininet and recreates all switch agents.
    """
    old_net = get_mininet()
    topo = get_shadow_topology()
    team = get_team()
    model = get_worker_model()
    
    # 1. Teardown existing network
    if old_net:
        old_net.stop()
        
    # Crucial: Scrub the Linux kernel of old veth pairs and OVS configurations
    cleanup()

    # 2. Build fresh Mininet instance
    net = Mininet(controller=Controller, link=TCLink)
    set_mininet(net) # Update the global context
    
    # 3. Apply Hosts
    for h_name, h_conf in topo["hosts"].items():
        if h_conf.get("ip"):
            net.addHost(h_name, ip=h_conf["ip"])
        else:
            net.addHost(h_name)
            
    # 4. Apply Switches
    for s_name in topo["switches"].keys():
        net.addSwitch(s_name, failMode='standalone')
        
    # 5. Apply Links with Configs
    for link in topo["links"]:
        n1 = net.get(link["node1"])
        n2 = net.get(link["node2"])
        net.addLink(n1, n2, **link["params"])
        
    # 6. Start the network
    net.start()
    
    # 7. Rebuild the Agent Team
    if team and model:
        # Filter out all existing switch agents based on an identifier 
        # (Assuming your switch agents have 'Switch' in their name)
        team.members = [m for m in team.members if "Switch" not in m.name]
        
        # Spawn fresh agents for the new topology
        for s_name in topo["switches"].keys():
            agent = make_switch_agent(name=s_name, neighbors=[], model=model)
            team.members.append(agent)
            
    return "Topology successfully deployed! Network restarted and fresh switch agents initialized."

@tool
def add_host_tool(name: str, ip: Optional[str] = None) -> str:
    """Draft a host to be added to the network."""
    topo = get_shadow_topology()
    
    if name in topo["hosts"] or name in topo["switches"]:
        return f"Node {name} already exists in the shadow topology."
        
    topo["hosts"][name] = {"ip": ip} if ip else {}
    return f"Host {name} added to shadow topology. Run the deploy tool to apply changes."

@tool
def add_switch_tool(name: str) -> str:
    """Draft a switch to be added to the network."""
    topo = get_shadow_topology()
    
    if name in topo["hosts"] or name in topo["switches"]:
        return f"Node {name} already exists in the shadow topology."
        
    topo["switches"][name] = {}
    return f"Switch {name} added to shadow topology. Run the deploy tool to apply changes."

@tool
def add_link_tool(node1: str, node2: str, bw: Optional[int] = None, delay: Optional[str] = None, loss: Optional[int] = None) -> str:
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
def remove_node_tool(name: str) -> str:
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
def remove_link_tool(node1: str, node2: str) -> str:
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