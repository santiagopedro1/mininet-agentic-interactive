from shutil import get_terminal_size
from time import time
from typing import Any, Callable, Optional

from agno.run.team import TeamRunOutput
from agno.utils.log import logger
from agno.agent import Agent
from agno.team import Team

def run_metrics(run_output: TeamRunOutput) -> None:
    """Post-hook to print run metrics like debug mode."""
    if not run_output.metrics:
        return None
    
    details = run_output.metrics.details
    if details is not None and "model" in details:
        model = details.get("model")
        if model and model[0] is not None and hasattr(model[0], "provider_metrics"):
            metrics = model[0].provider_metrics
            if metrics is not None:
                nr = (get_terminal_size().columns - 29) / 2
                print(f"{'=' * int(nr)} METRICS {'=' * int(nr)}")
                logger.info(f"Total duration: {metrics['total_duration'] / 1e9:.2f}s")
                logger.info(f"Load duration: {metrics['load_duration'] / 1e9:.2f}s")
                logger.info(f"Prompt eval duration: {metrics['prompt_eval_duration'] / 1e9:.2f}s")
                logger.info(f"Eval duration: {metrics['eval_duration'] / 1e9:.2f}s")
                print(f"{'=' * int(nr)}========={'=' * int(nr)}\n")
    else:
        return None
    
    

def tool_metrics(
    function_name: str,
    function_call: Callable,
    arguments: dict[str, Any],
    agent: Optional[Agent] = None,
    team: Optional[Team] = None,
):
    caller = getattr(agent, "name", None) or getattr(team, "name", None) or "unknown"

    if function_name == "delegate_task_to_member":
        member = arguments.get("member_id", "unknown")
        logger.info(f"{caller} delegated to {member}")
        result = function_call(**arguments)

    else:
        logger.info(f"{caller} used tool {function_name}: {arguments}")
        start = time()
        result = function_call(**arguments)
        logger.info(f"Tool {function_name} took {time() - start:.2f}s\n\n")

    
    return result