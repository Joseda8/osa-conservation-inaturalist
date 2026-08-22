export const DASHBOARD_SECTIONS = [
  { description: "Observation trends across Costa Rica.", id: "national-trends", label: "National trends" },
  { description: "Observations from OSA Conservation projects.", id: "osa-stats", label: "OSA stats" },
];

export const OSA_STATS_REPORTS = [
  { fileName: "abs-vs-obs-observations-by-day.csv", id: "observations-by-day", label: "Observations per day" },
  { fileName: "abs-vs-obs-observation-counts.csv", id: "observation-counts", label: "Observations per project", relatedDownloads: [{ fileName: "abs-vs-obs-duplicate-observations.csv", id: "duplicate-observations", label: "Download duplicate observations CSV" }], visualization: { ariaLabel: "Pie chart of observations per project", categoryColumn: "project_alias", categoryLabels: { abs: "ABS", obs: "OBS" }, summaryItems: [{ label: "Duplicate observations", sourceId: "duplicate-observations", valueColumn: "duplicate_observation_count", valueLabel: "observations" }], totalLabel: "Total observations", type: "pie", valueColumn: "observation_count", valueLabel: "observations" } },
  { fileName: "abs-vs-obs-quality-grades.csv", id: "quality-grades", label: "Quality grades" },
];

export const OSA_STATS_DATA_FILES = [
  ...OSA_STATS_REPORTS.map(({ fileName, id, label }) => ({ fileName, id, label })),
  ...OSA_STATS_REPORTS.flatMap((report) => report.relatedDownloads ?? []),
];
