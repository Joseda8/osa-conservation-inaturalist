export const DASHBOARD_SECTIONS = [
  { description: "Observation trends across Costa Rica.", id: "national-trends", label: "National trends" },
  { description: "Observations from OSA Conservation projects.", id: "osa-stats", label: "OSA stats" },
];

export const OSA_STATS_REPORTS = [
  { fileName: "abs-vs-obs-observations-by-day.csv", id: "observations-by-day", label: "Observations per day", sectionId: "osa-stats", visualization: { ariaLabel: "Time series comparing ABS and OBS observations", dateColumn: "observed_date", seriesColumn: "project_alias", seriesLabels: { abs: "ABS", obs: "OBS" }, type: "time-series", valueColumn: "observation_count", valueLabel: "observations" } },
  { fileName: "abs-vs-obs-observation-counts.csv", id: "observation-counts", label: "Observations per project", relatedDownloads: [{ fileName: "abs-vs-obs-duplicate-observations.csv", id: "duplicate-observations", label: "Download duplicate observations CSV" }], sectionId: "osa-stats", visualization: { ariaLabel: "Pie chart of observations per project", categoryColumn: "project_alias", categoryLabels: { abs: "ABS", obs: "OBS" }, summaryItems: [{ label: "Duplicate observations", sourceId: "duplicate-observations", valueColumn: "duplicate_observation_count", valueLabel: "observations" }], totalLabel: "Total observations", type: "pie", valueColumn: "observation_count", valueLabel: "observations" } },
  { fileName: "abs-vs-obs-quality-grades.csv", id: "quality-grades", label: "Quality grades", sectionId: "osa-stats", visualization: { ariaLabel: "Grouped bar chart comparing ABS and OBS observations by quality grade", categoryColumn: "quality_grade", categoryLabels: { casual: "Casual", needs_id: "Needs ID", research: "Research grade" }, seriesColumn: "project_alias", seriesLabels: { abs: "ABS", obs: "OBS" }, type: "grouped-bar", valueColumn: "observation_count", valueLabel: "observations" } },
];

export const OSA_STATS_DATA_FILES = [
  ...OSA_STATS_REPORTS.map(({ fileName, id, label }) => ({ fileName, id, label })),
  ...OSA_STATS_REPORTS.flatMap((report) => report.relatedDownloads ?? []),
];
