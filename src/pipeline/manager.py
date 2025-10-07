import logging

from importlib import import_module
from pipeline.utils.debug import debug_tools

logger = logging.getLogger(__name__)

class PipelineManager:
    def __init__(self, steps):
        self.steps = steps

    def run(self, ctx):
        # print(f"\n ------ >>> DEBUG_TOOLS : {debug_tools()}\n --- ctx : {ctx}")
        return self._run(0, ctx)

    def _run(self, idx, ctx):
        if idx >= len(self.steps):
            return True
        step = self.steps[idx]

        logger.debug(f"Running Pipeline Manager Step : {type(step).__name__}")
        # print(f" --- Running Pipeline Manager Step : {type(step).__name__}")

        def next(code):
            if code == 0 :
                self._run(idx+1, ctx)

        step.execute(ctx, next)
        
        return False
                        