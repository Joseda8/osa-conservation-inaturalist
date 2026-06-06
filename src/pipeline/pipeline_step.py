"""Pipeline step interface.

@file pipeline_step.py
@brief Defines the interface implemented by pipeline steps.
"""

from typing import Protocol

from .pipeline_context import PipelineContext


class PipelineStep(Protocol):
    """Interface for pipeline steps."""

    name: str

    def run(self, pipeline_context: PipelineContext):
        """Run this pipeline step.

        @param pipeline_context Shared pipeline state.
        """
