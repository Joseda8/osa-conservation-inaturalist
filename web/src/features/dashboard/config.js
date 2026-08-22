export const DASHBOARD_SECTIONS = [
  { description: "Observations from OSA Conservation projects.", id: "osa-stats", label: "OSA stats" },
  { description: "Observation trends across Costa Rica.", id: "national-trends", label: "National trends" },
];

export const OSA_STATS_REPORTS = [
  { fileName: "abs-vs-obs-observation-counts.csv", id: "observation-counts", label: "Observations per project", visualization: { ariaLabel: "Pie chart of observations per project", categoryColumn: "project_alias", totalLabel: "Total observations", type: "pie", valueColumn: "observation_count", valueLabel: "observations" } },
  { fileName: "abs-vs-obs-observations-by-day.csv", id: "observations-by-day", label: "Observations per day" },
  { fileName: "abs-vs-obs-duplicate-observations.csv", id: "duplicate-observations", label: "Duplicate observations" },
  { fileName: "abs-vs-obs-quality-grades.csv", id: "quality-grades", label: "Quality grades" },
];
