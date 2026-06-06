"""Project pipeline entry point.

@file main.py
@brief Runs the configured OSA iNaturalist data pipeline.
"""

import argparse
from datetime import date, datetime, time, timedelta

from inaturalist_client import OSA_PROJECTS, ProjectDownloadSummary
from pipeline import Pipeline, PipelineContext
from pipeline.pipeline_step import PipelineStep
from pipeline.steps import DownloadRawDataStep, LoadRawDataToDatabaseStep, MigrateDatabaseStep


_STEP_FACTORIES = {
    DownloadRawDataStep.name: DownloadRawDataStep,
    LoadRawDataToDatabaseStep.name: LoadRawDataToDatabaseStep,
    MigrateDatabaseStep.name: MigrateDatabaseStep,
}

_DEFAULT_STEP_NAMES = [
    DownloadRawDataStep.name,
    MigrateDatabaseStep.name,
    LoadRawDataToDatabaseStep.name,
]


def _parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    @return Parsed command-line arguments.
    """
    argument_parser = argparse.ArgumentParser(description="Run the OSA iNaturalist data pipeline.")
    argument_parser.add_argument(
        "--steps",
        nargs="+",
        choices=sorted(_STEP_FACTORIES.keys()),
        default=_DEFAULT_STEP_NAMES,
        help="Pipeline steps to run, in the order provided.",
    )
    argument_parser.add_argument(
        "--list-steps",
        action="store_true",
        help="List available pipeline steps and exit.",
    )
    argument_parser.add_argument(
        "--per-page",
        type=int,
        default=100,
        help="Requested observations per API batch.",
    )
    argument_parser.add_argument(
        "--request-cooldown",
        type=float,
        default=1.1,
        help="Seconds to wait after each successful API request.",
    )
    argument_parser.add_argument(
        "--failure-cooldown",
        type=float,
        default=60.0,
        help="Seconds to wait after failed API requests before retrying.",
    )
    argument_parser.add_argument(
        "--download-mode",
        choices=("incremental", "full"),
        default="incremental",
        help="Use incremental updated-since downloads or full project downloads.",
    )
    argument_parser.add_argument(
        "--updated-since",
        default=None,
        help="Override incremental cutoff as an ISO datetime. Defaults to previous local midnight.",
    )
    return argument_parser.parse_args()


def _build_steps(step_names: list[str]) -> list[PipelineStep]:
    """Build pipeline step instances from step names.

    @param step_names Names of pipeline steps to build.
    @return Pipeline step instances.
    """
    return [_STEP_FACTORIES[step_name]() for step_name in step_names]


def _print_available_steps():
    """Print the names of available pipeline steps."""
    for step_name in sorted(_STEP_FACTORIES.keys()):
        print(step_name)


def _print_download_summaries(download_summaries: list[ProjectDownloadSummary]):
    """Print a short summary of downloaded project data.

    @param download_summaries Download summaries created by the pipeline.
    """
    for project_summary in download_summaries:
        print(
            f"{project_summary.project_alias}: "
            f"{project_summary.page_count} pages, "
            f"{project_summary.total_results} observations, "
            f"{len(project_summary.saved_file_paths)} files"
        )


def _get_incremental_updated_since(arguments: argparse.Namespace) -> datetime | str | None:
    """Get the incremental updated-since cutoff.

    @param arguments Parsed command-line arguments.
    @return Updated-since cutoff, or None for full downloads.
    """
    if arguments.download_mode == "full":
        return None

    if arguments.updated_since is not None:
        return arguments.updated_since

    local_timezone = datetime.now().astimezone().tzinfo
    previous_local_date = date.today() - timedelta(days=1)
    return datetime.combine(previous_local_date, time.min, tzinfo=local_timezone)


def main():
    """Run the configured OSA data pipeline."""
    arguments = _parse_arguments()
    if arguments.list_steps:
        _print_available_steps()
        return

    pipeline_context = PipelineContext(
        project_configs=OSA_PROJECTS,
        per_page=arguments.per_page,
        request_cooldown_seconds=arguments.request_cooldown,
        failure_cooldown_seconds=arguments.failure_cooldown,
        download_mode=arguments.download_mode,
        updated_since=_get_incremental_updated_since(arguments),
    )
    pipeline = Pipeline(steps=_build_steps(arguments.steps))
    pipeline.run(pipeline_context)
    _print_download_summaries(pipeline_context.download_summaries)


if __name__ == "__main__":
    main()
