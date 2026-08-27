"""Project pipeline entry point.

@file main.py
@brief Runs the configured OSA iNaturalist data pipeline.
"""

import argparse
from calendar import monthrange
from datetime import date, datetime, time, timedelta

from inaturalist_client import OSA_PROJECTS, ProjectDownloadSummary
from pipeline import Pipeline, PipelineContext
from pipeline.constants import DATA_UPDATE_PIPELINE_STEP_NAMES, DEFAULT_DOWNLOAD_MODE, DEFAULT_FAILURE_COOLDOWN_SECONDS, DEFAULT_LIST_STEPS, DEFAULT_LOAD_DATE, DEFAULT_NAMED_PIPELINE, DEFAULT_OBSERVED_DATE_END, DEFAULT_OBSERVED_DATE_START, DEFAULT_OBSERVATIONS_PER_PAGE, DEFAULT_PIPELINE_MONTH, DEFAULT_PIPELINE_STEP_NAMES, DEFAULT_PIPELINE_YEAR, DEFAULT_REQUEST_COOLDOWN_SECONDS, DEFAULT_SELECTED_PIPELINE_STEPS, DEFAULT_TAXONOMY_MODE, DEFAULT_TREND_END_MONTH, DEFAULT_TREND_END_YEAR, DEFAULT_TREND_MODE, DEFAULT_TREND_MONTH, DEFAULT_TREND_YEAR, DEFAULT_UPDATED_SINCE, GOOGLE_AUTH_PIPELINE_NAME, GOOGLE_AUTH_PIPELINE_STEP_NAMES, HISTORICAL_LOAD_PIPELINE_NAME, MONTHLY_UPDATE_PIPELINE_NAME
from pipeline.pipeline_step import PipelineStep
from pipeline.steps import (
    DownloadRawDataStep,
    DownloadTrendsStep,
    EnrichTaxonomyStep,
    LoadRawDataToDatabaseStep,
    MigrateDatabaseStep,
    ReconcileProjectObservationsStep,
    AnalyzeAndUploadToDriveStep,
    AuthenticateWithGoogleStep,
    RefreshGitHubPagesStep,
)


_STEP_FACTORIES = {
    DownloadRawDataStep.name: DownloadRawDataStep,
    DownloadTrendsStep.name: DownloadTrendsStep,
    EnrichTaxonomyStep.name: EnrichTaxonomyStep,
    LoadRawDataToDatabaseStep.name: LoadRawDataToDatabaseStep,
    MigrateDatabaseStep.name: MigrateDatabaseStep,
    ReconcileProjectObservationsStep.name: ReconcileProjectObservationsStep,
    AnalyzeAndUploadToDriveStep.name: AnalyzeAndUploadToDriveStep,
    AuthenticateWithGoogleStep.name: AuthenticateWithGoogleStep,
    RefreshGitHubPagesStep.name: RefreshGitHubPagesStep,
}

def _parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    @return Parsed command-line arguments.
    """
    argument_parser = argparse.ArgumentParser(description="Run the OSA iNaturalist data pipeline.")
    argument_parser.add_argument("--steps", nargs="+", choices=sorted(_STEP_FACTORIES.keys()), default=DEFAULT_SELECTED_PIPELINE_STEPS, help="Pipeline steps to run, in the order provided.")
    argument_parser.add_argument("--pipeline", choices=(GOOGLE_AUTH_PIPELINE_NAME, HISTORICAL_LOAD_PIPELINE_NAME, MONTHLY_UPDATE_PIPELINE_NAME), default=DEFAULT_NAMED_PIPELINE, help="Named pipeline to run instead of individual steps.")
    argument_parser.add_argument("--year", type=int, default=DEFAULT_PIPELINE_YEAR, help="Calendar year processed by a named pipeline.")
    argument_parser.add_argument("--month", type=int, choices=range(1, 13), default=DEFAULT_PIPELINE_MONTH, help="Calendar month processed by a named pipeline.")
    argument_parser.add_argument("--list-steps", action="store_true", default=DEFAULT_LIST_STEPS, help="List available pipeline steps and exit.")
    argument_parser.add_argument("--per-page", type=int, default=DEFAULT_OBSERVATIONS_PER_PAGE, help="Requested observations per API batch.")
    argument_parser.add_argument("--request-cooldown", type=float, default=DEFAULT_REQUEST_COOLDOWN_SECONDS, help="Seconds to wait after each successful API request.")
    argument_parser.add_argument("--failure-cooldown", type=float, default=DEFAULT_FAILURE_COOLDOWN_SECONDS, help="Seconds to wait after failed API requests before retrying.")
    argument_parser.add_argument("--download-mode", choices=("incremental", "full"), default=DEFAULT_DOWNLOAD_MODE, help="Use incremental updated-since downloads or full project downloads.")
    argument_parser.add_argument("--updated-since", default=DEFAULT_UPDATED_SINCE, help="Override incremental cutoff as an ISO datetime. Defaults to previous local midnight.")
    argument_parser.add_argument("--observed-date-start", type=date.fromisoformat, default=DEFAULT_OBSERVED_DATE_START, help="First observed date for a bounded observation download, formatted as YYYY-MM-DD.")
    argument_parser.add_argument("--observed-date-end", type=date.fromisoformat, default=DEFAULT_OBSERVED_DATE_END, help="Final observed date for a bounded observation download, formatted as YYYY-MM-DD.")
    argument_parser.add_argument("--load-date", default=DEFAULT_LOAD_DATE, help="Only load raw JSON files for this snapshot date, formatted as YYYYMMDD.")
    argument_parser.add_argument("--trend-year", type=int, default=DEFAULT_TREND_YEAR, help="First year of the monthly trend period range to download.")
    argument_parser.add_argument("--trend-month", type=int, choices=range(1, 13), default=DEFAULT_TREND_MONTH, help="First month of the monthly trend period range to download.")
    argument_parser.add_argument("--trend-end-year", type=int, default=DEFAULT_TREND_END_YEAR, help="Final year of a bounded monthly trend download.")
    argument_parser.add_argument("--trend-end-month", type=int, choices=range(1, 13), default=DEFAULT_TREND_END_MONTH, help="Final month of a bounded monthly trend download.")
    argument_parser.add_argument("--trend-mode", choices=("since", "historical"), default=DEFAULT_TREND_MODE, help="Download trends since a starting month or the full available history.")
    argument_parser.add_argument("--taxonomy-mode", choices=("missing", "full"), default=DEFAULT_TAXONOMY_MODE, help="Enrich missing taxonomy nodes or refresh all stored taxa.")
    parsed_arguments = argument_parser.parse_args()
    _configure_named_pipeline(argument_parser, parsed_arguments)
    _validate_observation_date_arguments(argument_parser, parsed_arguments)
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
        print(f"{project_summary.project_alias}: {project_summary.page_count} pages, {project_summary.total_results} observations, {len(project_summary.saved_file_paths)} files")


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


def _configure_named_pipeline(argument_parser: argparse.ArgumentParser, arguments: argparse.Namespace):
    """Configure a named pipeline from its calendar period.

    @param argument_parser Argument parser used to report CLI errors.
    @param arguments Parsed command-line arguments.
    """
    if arguments.pipeline is None:
        if arguments.steps is None:
            arguments.steps = DEFAULT_PIPELINE_STEP_NAMES
        if arguments.year is not None or arguments.month is not None:
            argument_parser.error("--year and --month require --pipeline monthly-update")
        return

    if arguments.steps is not None:
        argument_parser.error("--pipeline cannot be combined with --steps")
    if arguments.pipeline == HISTORICAL_LOAD_PIPELINE_NAME:
        if arguments.year is not None or arguments.month is not None:
            argument_parser.error("historical-load does not use --year or --month")
        _configure_historical_load(arguments)
        return
    if arguments.pipeline == GOOGLE_AUTH_PIPELINE_NAME:
        if arguments.year is not None or arguments.month is not None:
            argument_parser.error("auth-with-google does not use --year or --month")
        arguments.steps = GOOGLE_AUTH_PIPELINE_STEP_NAMES
        return
    if arguments.year is None or arguments.month is None:
        argument_parser.error("monthly-update requires --year and --month")

    month_start, month_end = _get_month_period(arguments.year, arguments.month)
    arguments.steps = DATA_UPDATE_PIPELINE_STEP_NAMES
    arguments.download_mode = "full"
    arguments.updated_since = None
    arguments.observed_date_start = month_start
    arguments.observed_date_end = month_end
    arguments.load_date = date.today().strftime("%Y%m%d")
    arguments.trend_mode = "since"
    arguments.trend_year = arguments.year
    arguments.trend_month = arguments.month
    arguments.trend_end_year = arguments.year
    arguments.trend_end_month = arguments.month


def _configure_historical_load(arguments: argparse.Namespace):
    """Configure the historical-load pipeline.

    @param arguments Parsed command-line arguments.
    """
    arguments.steps = DATA_UPDATE_PIPELINE_STEP_NAMES
    arguments.download_mode = "full"
    arguments.updated_since = None
    arguments.observed_date_start = None
    arguments.observed_date_end = None
    arguments.load_date = date.today().strftime("%Y%m%d")
    arguments.trend_mode = "historical"
    arguments.trend_year = None
    arguments.trend_month = None
    arguments.trend_end_year = None
    arguments.trend_end_month = None


def _validate_observation_date_arguments(argument_parser: argparse.ArgumentParser, arguments: argparse.Namespace):
    """Validate bounded observation-download arguments.

    @param argument_parser Argument parser used to report CLI errors.
    @param arguments Parsed command-line arguments.
    """
    if DownloadRawDataStep.name not in arguments.steps:
        return

    has_observed_date_start = arguments.observed_date_start is not None
    has_observed_date_end = arguments.observed_date_end is not None
    if has_observed_date_start != has_observed_date_end:
        argument_parser.error("--observed-date-start and --observed-date-end must be provided together")
    if not has_observed_date_start:
        return
    if arguments.download_mode != "full":
        argument_parser.error("bounded observation downloads require --download-mode full")
    if arguments.updated_since is not None:
        argument_parser.error("bounded observation downloads cannot use --updated-since")
    if arguments.observed_date_start > arguments.observed_date_end:
        argument_parser.error("--observed-date-start cannot be later than --observed-date-end")


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
    has_trend_end_year = arguments.trend_end_year is not None
    has_trend_end_month = arguments.trend_end_month is not None
    if arguments.trend_mode == "historical":
        if has_trend_year or has_trend_month or has_trend_end_year or has_trend_end_month:
            argument_parser.error(
                "historical trend mode does not use trend start or end arguments"
            )
        arguments.trend_period_start = None
        arguments.trend_period_end = _get_last_completed_month_end()
        return

    if not has_trend_year or not has_trend_month:
        argument_parser.error("since trend mode requires --trend-year and --trend-month")
    if has_trend_end_year != has_trend_end_month:
        argument_parser.error("--trend-end-year and --trend-end-month must be provided together")

    trend_period_start, trend_start_month_end = _get_month_period(
        arguments.trend_year,
        arguments.trend_month,
    )
    trend_period_end = _get_last_completed_month_end()
    if has_trend_end_year:
        _, trend_period_end = _get_month_period(arguments.trend_end_year, arguments.trend_end_month)
    if trend_start_month_end >= date.today() or trend_period_end >= date.today():
        argument_parser.error("download-trends can only include completed months")
    if trend_period_start > trend_period_end:
        argument_parser.error("trend start month cannot be later than trend end month")

    arguments.trend_period_start = trend_period_start
    arguments.trend_period_end = trend_period_end


def _get_month_period(year: int, month: int) -> tuple[date, date]:
    """Get the first and last date for one calendar month.

    @param year Calendar year.
    @param month Calendar month.
    @return First and last date of the month.
    """
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


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
        observed_date_start=arguments.observed_date_start,
        observed_date_end=arguments.observed_date_end,
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
