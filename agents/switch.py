from agno.agent import Agent

from tools.switch_stats import get_switch_interface_metrics

def make_switch_agent(name, neighbors, model):
    return Agent(
        name=f"Switch-{name} Agent",
        role="You are a switch in a Mininet network topology.",
        model=model,
        tools=[get_switch_interface_metrics],
        instructions=[
        f"You are switch {name} in a mininet network topology.",
        f"These are your neighbors: {neighbors}.",
        "Respond using only the result from tools, do not provide analysis or interpretation.",
        "Do not summarize or explain the data, just return it as is."
        ]
    )