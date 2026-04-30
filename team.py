from agno.team import Team, TeamMode
from agno.models.ollama import Ollama

from config import OLLAMA_BASE_URL, COORDINATOR_MODEL, WORKER_MODEL
from topology import TOPOLOGY, topology_to_text
from agents.switch import make_switch_agent
from agents.network_ops import make_network_agent

from tools.routing import routing_tool

from tools.context import get_mininet

def get_switch_neighbors(switch_name: str):
    net = get_mininet()
    if net is None:
        raise RuntimeError("Mininet not initialized")

    try:
        sw = net.get(switch_name)
    except Exception:
        raise ValueError(f"Switch {switch_name} not found")

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

def build_models():
    coordinator = Ollama(
        id=COORDINATOR_MODEL,
        host=OLLAMA_BASE_URL
    )

    worker = Ollama(
        id=WORKER_MODEL,
        host=OLLAMA_BASE_URL,
        keep_alive="2m"
    )

    return coordinator, worker

def get_switch_names(net):
    return [sw.name for sw in net.switches]

def build_switch_agents(worker_model, switch_names):
    agents = []

    for sw in switch_names:
        agent = make_switch_agent(name=sw, neighbors=get_switch_neighbors(sw), model=worker_model)
        agents.append(agent)

    return agents

def build_team():
    coordinator_model, worker_model = build_models()

    switch_names = ["s1", "s2", "s3"]

    switch_agents = build_switch_agents(worker_model, switch_names)


    network_agent = make_network_agent(worker_model)

    team = Team(
        name="Mininet Team",
        model=coordinator_model,
        mode=TeamMode.coordinate,
        members=[network_agent, *switch_agents],
        tools=[routing_tool],
        debug_mode=True,
        instructions=f"""
        You are managing a network.

        Topology:
        {topology_to_text(TOPOLOGY)}

        Rules:
        - Use routing_tool for path computation
        - Use NetworkOps for connectivity tests
        - Query switch agents only for local insights
        """
    )

    return team