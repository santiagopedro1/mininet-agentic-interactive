from agno.team import Team, TeamMode
from agno.models.ollama import Ollama

from config import OLLAMA_BASE_URL, COORDINATOR_MODEL, WORKER_MODEL

from agents.switch import make_switch_agent
from agents.net_diag import make_network_diagnostics_agent
from agents.net_manager import make_network_manager_agent

from utils.context import get_mininet, set_team, set_worker_model
from utils.neighbors import get_switch_neighbors
from utils.hooks import run_metrics, tool_metrics
from tools.net_management import list_topology_tool

def build_models():
    coordinator = Ollama(
        id=COORDINATOR_MODEL,
        host=OLLAMA_BASE_URL
    )

    worker = Ollama(
        id=WORKER_MODEL,
        host=OLLAMA_BASE_URL,
    )

    return coordinator, worker

def get_switch_names(net):
    if not net:
        return []
    return [sw.name for sw in net.switches]

def build_switch_agents(worker_model, switch_names):
    agents = []

    for sw in switch_names:
        agent = make_switch_agent(name=sw, neighbors=get_switch_neighbors(sw), model=worker_model)
        agents.append(agent)

    return agents

def build_team():
    coordinator_model, worker_model = build_models()
    set_worker_model(worker_model)

    net = get_mininet()
    switch_names = get_switch_names(net)

    switch_agents = build_switch_agents(worker_model, switch_names)

    network_agent = make_network_diagnostics_agent(worker_model)
    network_manager_agent = make_network_manager_agent(worker_model)

    team = Team(
        name="Mininet Team",
        model=coordinator_model,
        mode=TeamMode.coordinate,
        members=[network_agent, network_manager_agent, *switch_agents],
        tools=[list_topology_tool],
        tool_hooks=[tool_metrics],
        post_hooks=[run_metrics],
        markdown=True,
        instructions=[
            "You are a team managing a Mininet network topology.",
            "Do not delegate analysis or interpretation to other agents; perform it yourself using the data they provide.",
            "Do not request additional information from agents unless required by the user's request.",
            "Numeric fidelity is mandatory. Preserve all user-provided numeric parameters exactly unless the user explicitly requests optimization or correction.",
            "Provide all relevant available information unless the user requests otherwise.",
            "network_agent executes network operations and gathers topology telemetry.",
            "switch_agents monitor their assigned switches and provide telemetry data.",
            "network_manager_agent handles topology modifications, including adding/removing nodes and links.",
            "Use list_topology_tool when you need to confirm host or switch names.",
            "Before delegating a task, ensure the receiving agent has all required context.",
            "All ping and iperf operations must include an explicit full path. If the user does not specify one, use the shortest path by default and include the complete path in the agent prompt.",
            "If the user specifies path constraints, compute a valid path satisfying those constraints and provide the complete path explicitly.",
        ]
    )

    set_team(team)
    return team
