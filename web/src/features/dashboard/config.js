export const DASHBOARD_SECTIONS = [
  { description: "Observation trends across Costa Rica.", id: "national-trends", label: "National trends" },
  { description: "Observations from OSA Conservation projects.", id: "osa-stats", label: "OSA stats" },
];

export const OSA_STATS_REPORTS = [
  { fileName: "abs-vs-obs-observations-by-day.csv", id: "observations-by-day", label: "Observations per day", sectionId: "osa-stats", visualization: { ariaLabel: "Time series comparing ABS, OBS, and aggregated observations", dateColumn: "observed_date", seriesColumn: "project_alias", seriesLabels: { abs: "ABS", aggregated: "Aggregated", obs: "OBS" }, seriesOrder: ["abs", "obs", "aggregated"], type: "time-series", valueColumn: "observation_count", valueLabel: "observations" } },
  { fileName: "abs-vs-obs-observation-counts.csv", id: "observation-counts", label: "Observations per project", relatedDownloads: [{ fileName: "abs-vs-obs-duplicate-observations.csv", id: "duplicate-observations", label: "Download duplicate observations CSV" }], sectionId: "osa-stats", visualization: { ariaLabel: "Pie chart of observations per project", categoryColumn: "project_alias", categoryLabels: { abs: "ABS", obs: "OBS" }, excludedCategories: ["aggregated"], summaryItems: [{ label: "Duplicate observations", sourceId: "duplicate-observations", valueColumn: "duplicate_observation_count", valueLabel: "observations" }], totalCategory: "aggregated", totalLabel: "Total observations", type: "pie", valueColumn: "observation_count", valueLabel: "observations" } },
  { fileName: "abs-vs-obs-quality-grades.csv", id: "quality-grades", label: "Quality grades", sectionId: "osa-stats", visualization: { annotationColumn: "project_observation_percentage", ariaLabel: "Grouped bar chart comparing ABS, OBS, and aggregated observations by quality grade", categoryColumn: "quality_grade", categoryLabels: { casual: "Casual", needs_id: "Needs ID", research: "Research grade" }, hiddenTotalSeries: ["aggregated"], seriesColumn: "project_alias", seriesLabels: { abs: "ABS", aggregated: "Aggregated", obs: "OBS" }, seriesOrder: ["abs", "obs", "aggregated"], totalColumn: "project_total_observation_count", totalLabel: "Total observations", totalObservationColumn: "total_observation_count", totalSeriesId: "aggregated", type: "grouped-bar", valueColumn: "observation_count", valueLabel: "observations" } },
  { fileName: "abs-vs-obs-species-reported-by-month.csv", id: "species-reported-over-time", label: "Species reported over time", sectionId: "osa-stats", visualization: { ariaLabel: "Monthly species reported by ABS, OBS, and aggregated observations", dateColumn: "period_start", defaultGrouping: "month", defaultRangePreset: "last-90", seriesColumn: "project_alias", seriesLabels: { abs: "ABS", aggregated: "Aggregated", obs: "OBS" }, seriesOrder: ["abs", "obs", "aggregated"], type: "time-series", valueColumn: "species_count", valueLabel: "species" } },
];

export const OSA_STATS_DATA_FILES = [
  ...OSA_STATS_REPORTS.map(({ fileName, id, label }) => ({ fileName, id, label })),
  ...OSA_STATS_REPORTS.flatMap((report) => report.relatedDownloads ?? []),
];
