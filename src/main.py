"""Project pipeline entry point.

@file main.py
@brief Runs the configured OSA iNaturalist data pipeline.
"""

import argparse
from calendar import monthrange
from datetime import date, datetime, time, timedelta

from inaturalist_client import OSA_PROJECTS, ProjectDownloadSummary
from pipeline import Pipeline, PipelineContext
from pipeline.pipeline_step import PipelineStep
from pipeline.steps import (
    DownloadRawDataStep,
    DownloadTrendsStep,
    EnrichTaxonomyStep,
    LoadRawDataToDatabaseStep,
    MigrateDatabaseStep,
    ReconcileProjectObservationsStep,
)


_STEP_FACTORIES = {
    DownloadRawDataStep.name: DownloadRawDataStep,
    DownloadTrendsStep.name: DownloadTrendsStep,
    EnrichTaxonomyStep.name: EnrichTaxonomyStep,
    LoadRawDataToDatabaseStep.name: LoadRawDataToDatabaseStep,
    MigrateDatabaseStep.name: MigrateDatabaseStep,
    ReconcileProjectObservationsStep.name: ReconcileProjectObservationsStep,
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
    argument_parser.add_argument(
        "--load-date",
        default=None,
        help="Only load raw JSON files for this snapshot date, formatted as YYYYMMDD.",
    )
    argument_parser.add_argument(
        "--trend-year",
        type=int,
        default=None,
        help="First year of the monthly trend period range to download.",
    )
    argument_parser.add_argument(
        "--trend-month",
        type=int,
        choices=range(1, 13),
        default=None,
        help="First month of the monthly trend period range to download.",
    )
    argument_parser.add_argument(
        "--trend-mode",
        choices=("since", "historical"),
        default="since",
        help="Download trends since a starting month or the full available history.",
    )
    argument_parser.add_argument(
        "--taxonomy-mode",
        choices=("missing", "full"),
        default="missing",
        help="Enrich missing taxonomy nodes or refresh all stored taxa.",
    )
    parsed_arguments = argument_parser.parse_args()
    _validate_trend_arguments(argument_parser, parsed_arguments)
    return parsed_arguments


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


def _validate_load_date(load_date: str | None) -> str | None:
    """Validate the optional raw data load date.

    @param load_date Date string formatted as YYYYMMDD.
    @return Validated load date, or None.
    """
    if load_date is None:
        return None

    datetime.strptime(load_date, "%Y%m%d")
    return load_date


def _validate_trend_arguments(
    argument_parser: argparse.ArgumentParser,
    arguments: argparse.Namespace,
):
    """Validate trend CLI arguments.

    @param argument_parser Argument parser used to report CLI errors.
    @param arguments Parsed command-line arguments.
    """
    if DownloadTrendsStep.name not in arguments.steps:
        return

    has_trend_year = arguments.trend_year is not None
    has_trend_month = arguments.trend_month is not None
    if arguments.trend_mode == "historical":
        if has_trend_year or has_trend_month:
            argument_parser.error(
                "historical trend mode does not use --trend-year or --trend-month"
            )
        arguments.trend_period_start = None
        arguments.trend_period_end = _get_last_completed_month_end()
        return

    if not has_trend_year or not has_trend_month:
        argument_parser.error("since trend mode requires --trend-year and --trend-month")

    trend_period_start, trend_start_month_end = _get_trend_period(
        arguments.trend_year,
        arguments.trend_month,
    )
    if trend_start_month_end >= date.today():
        argument_parser.error("download-trends can only start from a month that has ended")

    arguments.trend_period_start = trend_period_start
    arguments.trend_period_end = _get_last_completed_month_end()


def _get_trend_period(trend_year: int, trend_month: int) -> tuple[date, date]:
    """Get the first and last date for a monthly trend period.

    @param trend_year Trend period year.
    @param trend_month Trend period month.
    @return First and last date of the month.
    """
    last_day = monthrange(trend_year, trend_month)[1]
    return date(trend_year, trend_month, 1), date(trend_year, trend_month, last_day)


def _get_last_completed_month_end() -> date:
    """Get the last date of the most recent completed month.

    @return Last date of the previous month.
    """
    current_month_start = date.today().replace(day=1)
    return current_month_start - timedelta(days=1)


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
        load_date=_validate_load_date(arguments.load_date),
        trend_mode=arguments.trend_mode,
        trend_period_start=getattr(arguments, "trend_period_start", None),
        trend_period_end=getattr(arguments, "trend_period_end", None),
        taxonomy_mode=arguments.taxonomy_mode,
    )
    pipeline = Pipeline(steps=_build_steps(arguments.steps))
    pipeline.run(pipeline_context)
    _print_download_summaries(pipeline_context.download_summaries)


if __name__ == "__main__":
    main()
