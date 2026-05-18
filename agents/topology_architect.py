from agno.agent import Agent

from tools.net_management import add_host, add_switch, add_link, remove_link, remove_node, deploy_topology, list_topology
from utils.hooks import tool_metrics

def make_topology_architect_agent(model):
    return Agent(
        name="Topology Architect",
        role="Builds and modifies Mininet topologies.",
        model=model,
        tools=[add_host, add_switch, add_link, remove_node, remove_link, deploy_topology, list_topology],
        tool_hooks=[tool_metrics],
        instructions=[
            "Use this naming convention for hosts and switches: hosts as 'h1', 'h2', etc. and switches as 's1', 's2', etc, unless told otherwise.",
            "When adding a link, only specify bandwidth (bw), delay, and loss if specifically requested.",
            "Whenever you add a link with a delay, make sure to pass the parameter as string, eg.  200ms.",
            "The bandwidth (bw) parameter should be a float representing Mbps, for example, 100.0 for 100 Mbps.",
            "Do not analyze the network performance, your focus is on topology management.",
            "When asked to recreate a link, first remove the existing link and then create a new one with the updated parameters.",
            "Return tool outputs as JSON for the team coordinator.",
            "After adding all hosts, switches and links that a topology requires, run the deploy tool to apply the changes to the Mininet topology.",
        ]
    )
