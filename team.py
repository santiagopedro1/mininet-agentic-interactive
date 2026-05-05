import time
from typing import Any, Callable, Dict

from agno.utils.log import logger

from agno.team import Team, TeamMode
from agno.models.ollama import Ollama

from config import OLLAMA_BASE_URL, COORDINATOR_MODEL, WORKER_MODEL

from agents.switch import make_switch_agent
from agents.net_diag import make_network_diagnostics_agent
from agents.net_manager import make_network_manager_agent

from context import get_mininet, set_team, set_worker_model
from tools.net_management import list_topology_tool

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

def build_models():
    coordinator = Ollama(
        id=COORDINATOR_MODEL,
        host=OLLAMA_BASE_URL
    )

    worker = Ollama(
        id=WORKER_MODEL,
        host=OLLAMA_BASE_URL,
        keep_alive="5m"
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


# ── hooks ─────────────────────────────────────────────────────────────────────

def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """
    Tool hook that logs function calls and measures execution time.

    Args:
        function_name: Name of the function being called
        function_call: The actual function to call
        arguments: Arguments passed to the function

    Returns:
        The result of the function call
    """
    if function_name == "delegate_task_to_member":
        member_id = arguments.get("member_id")
        logger.info(f"Delegating task to member {member_id}")
        result = function_call(**arguments)
        return result

    # Start timer
    start_time = time.time()
    result = function_call(**arguments)
    # End timer
    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"Function {function_name} took {duration:.2f} seconds to execute")
    return result


def on_run_completed(run_output=None, **_):
    m = getattr(run_output, "metrics", None)
    if m is None:
        return

    duration = getattr(m, "duration", None)
    input_tok = getattr(m, "input_tokens", None)
    output_tok = getattr(m, "output_tokens", None)

    # collect model ids from details breakdown
    models = []
    details = getattr(m, "details", None) or {}
    for model_list in details.values():
        for mm in model_list:
            mid = getattr(mm, "id", None)
            if mid and mid not in models:
                models.append(mid)

    print(
        f"\n[metrics] time={duration:.2f}s" if duration else "\n[metrics]",
        f"  in={input_tok} out={output_tok} tokens" if input_tok is not None else "",
        f"  models={models}" if models else "",
    )

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
        debug_mode=True,
        tools=[list_topology_tool],
        tool_hooks=[logger_hook],
        post_hooks=[on_run_completed],
        markdown=True,
        instructions=[
            "You are a team of agents managing a Mininet network topology.",
            "Do not ask other agents for analysis or interpretation. You should to the analysis yourself based on the data you gather from team members' responses.",
            "Do not ask other agents for additional information that the user did not request.",
            "If the user did not ask for specific information, provide all avaiable information that you have access to which is relevant to the user's query.",
            "network_agent is responsible for executing network operations and gathering telemetry across the topology.",
            "switch_agents are responsible for monitoring their respective switches and providing telemetry data.",
            "network_manager_agent is responsible for topology changes (adding/removing nodes and links).",
            "use list_topology_tool to confirm the names of switches and hosts in the topology when needed.",
        ]
    )

    set_team(team)
    return team
