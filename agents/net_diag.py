from agno.agent import Agent
from tools.ping import ping_tool
from tools.iperf import run_iperf_test
from utils.hooks import tool_metrics

def make_network_diagnostics_agent(model):
    return Agent(
        name="Network Diagnostics Agent",
        role="Run pings and set up iperf tests on the Mininet network",
        model=model,
        tool_call_limit=1,
        tools=[ping_tool, run_iperf_test],
        tool_hooks=[tool_metrics],
        instructions=[
            "You run network diagnostics on a Mininet topology using the provided custom tools.",
            "Before any tool call, ensure you have the necessary context (e.g., host names, IPs) to avoid tool failures. If context is missing and has no default, stop and escalate the issue back to the team leader with a short error message.",
            "Do not analyze, summarize, or interpret the results.",
            "Return the tool output as a JSON object containing the raw measurement data for the team leader.",
            "If a tool fails, a host is unreachable, or required context is missing that has no default, stop and escalate the issue back to the team leader with a short error message.",
        ]
    )