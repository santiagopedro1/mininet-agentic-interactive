from agno.agent import Agent

from tools.net_management import add_host_tool, add_switch_tool, add_link_tool, remove_link_tool, remove_node_tool, deploy_topology_tool, list_topology_tool
from utils.hooks import tool_metrics

def make_network_manager_agent(model):
    return Agent(
        name="Network Manager Agent",
        role="You are responsible for managing the Mininet network topology dynamically.",
        model=model,
        use_json_mode=True,
        tools=[add_host_tool, add_switch_tool, add_link_tool, remove_node_tool, remove_link_tool, deploy_topology_tool, list_topology_tool],
        tool_hooks=[tool_metrics],
        instructions=[
            "You manage the Mininet network topology by creating, editing, and deleting hosts, switches, and links.",
            "When you create a switch, a corresponding agent is automatically created and added to the team to monitor it.",
            "Use this naming convention for hosts and switches: hosts as 'h1', 'h2', etc. and switches as 's1', 's2', etc.",
            "When adding a link, only specify bandwidth (bw), delay, and loss if specifically requested.",
            "Whenever you add a link with a delay, make sure to pass the parameter as string, eg.  200ms.",
            "The bandwidth (bw) parameter should be a float representing Mbps, for example, 100.0 for 100 Mbps.",
            "Do not analyze the network performance, your focus is on topology management.",
            "When asked to recreate a link, first remove the existing link and then create a new one with the updated parameters.",
            "Return tool outputs as JSON for the team coordinator.",
            "After adding all hosts, switches and links that a topology requires, run the deploy tool to apply the changes to the Mininet topology.",
        ]
    )
