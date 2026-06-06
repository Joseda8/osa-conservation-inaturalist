"""Pipeline runner.

@file pipeline.py
@brief Runs pipeline steps in order.
"""

from utils import LOGGER

from .pipeline_context import PipelineContext
from .pipeline_step import PipelineStep


class Pipeline:
    """Runs pipeline steps in order.

    @param steps Ordered pipeline steps.
    """

    def __init__(self, steps: list[PipelineStep]):
        """Create a pipeline.

        @param steps Ordered pipeline steps.
        """
        self._steps = steps

    def run(self, pipeline_context: PipelineContext):
        """Run all pipeline steps.

        @param pipeline_context Shared pipeline state.
        """
        for pipeline_step in self._steps:
            LOGGER.info("Starting pipeline step: %s", pipeline_step.name)
            pipeline_step.run(pipeline_context)
            LOGGER.info("Completed pipeline step: %s", pipeline_step.name)
