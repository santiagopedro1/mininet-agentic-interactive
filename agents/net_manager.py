from agno.agent import Agent
from tools.net_management import add_host_tool, add_switch_tool, add_link_tool, remove_link_tool, remove_node_tool, deploy_topology_tool, list_topology_tool

def make_network_manager_agent(model):
    return Agent(
        name="Network Manager Agent",
        role="You are responsible for managing the Mininet network topology dynamically.",
        model=model,
        use_json_mode=True,
        tools=[add_host_tool, add_switch_tool, add_link_tool, remove_node_tool, remove_link_tool, deploy_topology_tool, list_topology_tool],
        instructions=[
            "You manage the Mininet network topology by creating, editing, and deleting hosts, switches, and links.",
            "When you create a switch, a corresponding agent is automatically created and added to the team to monitor it.",
            "Use this naming convention for hosts and switches: hosts as 'h1', 'h2', etc. and switches as 's1', 's2', etc.",
            "Use 'list_topology_tool' to understand the current state before making changes or when requested.",
            "When adding a link, you can specify bandwidth (bw), delay, and loss if requested.",
            "Do not analyze the network performance, your focus is on topology management.",
            "Return tool outputs as JSON for the team coordinator.",
        ]
    )
