from agno.agent import Agent
from tools.ping import ping_tool

def make_network_diagnostics_agent(model):
    return Agent(
        name="Network Diagnostics Agent",
        role="Run pings and set up iperf tests on the Mininet network",
        model=model,
        use_json_mode=True,
        tools=[ping_tool],
        instructions=[
            "You run network diagnostics on a Mininet topology using the provided custom tools.",
            "Determine from the prompt whether to run a ping or an iperf test, and call the corresponding tool.",
            "Extract arguments (e.g., source host, destination host, duration, count) from the prompt. If any argument is missing, fall back to the configured default values.",
            "Do not analyze, summarize, or interpret the results.",
            "Return the tool output as a JSON object containing the raw measurement data for the team leader.",
            "If a tool fails, a host is unreachable, or required context is missing that has no default, stop and escalate the issue back to the team leader with a short error message.",
        ]
    )