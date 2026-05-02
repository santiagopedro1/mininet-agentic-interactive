from agno.agent import Agent

from tools.switch_stats import switch_stats_tool

def make_switch_agent(name, neighbors, model):
    return Agent(
        name=f"Switch-{name}",
        model=model,
        use_json_mode=True,
        tools=[switch_stats_tool],
        instructions=f"""
        You are switch {name}.
        You only know your neighbors: {neighbors}.

        Provide local reasoning only.
        Suggest next hops if asked.
        Do not assume global topology.
        """
    )