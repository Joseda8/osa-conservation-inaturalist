export const DASHBOARD_SECTIONS = [
  { description: "Observation trends across Costa Rica.", id: "national-trends", label: "National trends" },
  { description: "Observations from OSA Conservation projects.", id: "osa-stats", label: "OSA stats" },
];

export const DASHBOARD_REPORT_CATEGORIES = [
  { id: "observation-stats", label: "Observation stats", sectionId: "osa-stats" },
  { id: "observer-stats", label: "Observer stats", sectionId: "osa-stats" },
  { id: "species-stats", label: "Species stats", sectionId: "osa-stats" },
];

const PROJECT_OBSERVATION_SERIES = {
  seriesColumn: "project_alias",
  seriesLabels: { abs: "ABS", aggregated: "Aggregated", obs: "OBS" },
  seriesOrder: ["abs", "obs", "aggregated"],
};

function createFocalTaxaReport({ ariaLabel, dataSetLabel = "Species", dataSetOrder, fileName, id, label }) {
  return {
    categoryId: "species-stats",
    fileName,
    id,
    label,
    sectionId: "osa-stats",
    visualization: {
      ariaLabel,
      dataSetColumn: "taxon_id",
      dataSetLabel,
      dataSetLabelColumn: "english_name",
      dataSetOrder,
      dateColumn: "observed_date",
      defaultGrouping: "month",
      defaultRangePreset: "last-year",
      ...PROJECT_OBSERVATION_SERIES,
      type: "time-series",
      valueColumn: "observation_count",
      valueLabel: "observations",
    },
  };
}

export const OSA_STATS_REPORTS = [
  { categoryId: "observer-stats", fileName: "abs-vs-obs-active-observers.csv", id: "active-observers", infoText: "An active observer has uploaded at least one observation during the 365 days before this report was generated. The lifespan values are the active observers' average time between first and last observed dates.", label: "Active observers", sectionId: "osa-stats", visualization: { annotationColumn: "observer_percentage", ariaLabel: "Active and inactive observers in ABS, OBS, and aggregated observations", categoryColumn: "activity_status", categoryLabels: { active: "Active observers", inactive: "Inactive observers" }, seriesColumn: "project_alias", seriesLabels: { abs: "ABS", aggregated: "Aggregated", obs: "OBS" }, seriesOrder: ["abs", "obs", "aggregated"], seriesSummaryLabel: "active observers average lifespan", seriesSummaryValueLabel: "days", totalColumn: "average_active_observer_lifespan_days", type: "grouped-bar", valueColumn: "observer_count", valueLabel: "observers" } },
  { categoryId: "observation-stats", fileName: "abs-vs-obs-observations-by-day.csv", id: "observations-by-day", label: "Observations per day", sectionId: "osa-stats", visualization: { ariaLabel: "Time series comparing ABS, OBS, and aggregated observations", dateColumn: "observed_date", seriesColumn: "project_alias", seriesLabels: { abs: "ABS", aggregated: "Aggregated", obs: "OBS" }, seriesOrder: ["abs", "obs", "aggregated"], type: "time-series", valueColumn: "observation_count", valueLabel: "observations" } },
  { categoryId: "observation-stats", fileName: "abs-vs-obs-observation-counts.csv", id: "observation-counts", label: "Observations per project", relatedDownloads: [{ fileName: "abs-vs-obs-duplicate-observations.csv", id: "duplicate-observations", label: "Download duplicate observations CSV" }], sectionId: "osa-stats", visualization: { ariaLabel: "Pie chart of observations per project", categoryColumn: "project_alias", categoryLabels: { abs: "ABS", obs: "OBS" }, excludedCategories: ["aggregated"], summaryItems: [{ label: "Duplicate observations", sourceId: "duplicate-observations", valueColumn: "duplicate_observation_count", valueLabel: "observations" }], totalCategory: "aggregated", totalLabel: "Total observations", type: "pie", valueColumn: "observation_count", valueLabel: "observations" } },
  { categoryId: "observation-stats", fileName: "abs-vs-obs-quality-grades.csv", id: "quality-grades", label: "Quality grades", sectionId: "osa-stats", visualization: { annotationColumn: "project_observation_percentage", ariaLabel: "Grouped bar chart comparing ABS, OBS, and aggregated observations by quality grade", categoryColumn: "quality_grade", categoryLabels: { casual: "Casual", needs_id: "Needs ID", research: "Research grade" }, hiddenTotalSeries: ["aggregated"], seriesColumn: "project_alias", seriesLabels: { abs: "ABS", aggregated: "Aggregated", obs: "OBS" }, seriesOrder: ["abs", "obs", "aggregated"], totalColumn: "project_total_observation_count", totalLabel: "Total observations", totalObservationColumn: "total_observation_count", totalSeriesId: "aggregated", type: "grouped-bar", valueColumn: "observation_count", valueLabel: "observations" } },
  { categoryId: "observer-stats", fileName: "abs-vs-obs-observers-by-month.csv", id: "observers-over-time", label: "Observers over time", sectionId: "osa-stats", visualization: { allowedGroupings: ["month", "year"], ariaLabel: "Observers joining ABS, OBS, and aggregated observations over time", dateColumn: "period_start", defaultGrouping: "month", defaultRangePreset: "last-90", measures: [{ id: "new", label: "New observers", valueColumn: "new_observer_count", valueLabel: "observers" }, { id: "cumulative", label: "Cumulative total", valueAggregation: "latest", valueColumn: "cumulative_observer_count", valueLabel: "observers" }], seriesColumn: "project_alias", seriesLabels: { abs: "ABS", aggregated: "Aggregated", obs: "OBS" }, seriesOrder: ["abs", "obs", "aggregated"], type: "time-series", valueColumn: "new_observer_count", valueLabel: "observers" } },
  { categoryId: "species-stats", fileName: "abs-vs-obs-species-reported-by-month.csv", id: "species-reported-over-time", label: "Species reported over time", sectionId: "osa-stats", visualization: { allowedGroupings: ["month", "year"], ariaLabel: "Research-grade species reported by ABS, OBS, and aggregated observations", dateColumn: "period_start", defaultGrouping: "month", defaultRangePreset: "last-90", measures: [{ id: "reported", label: "Reported in period", valueColumn: "species_count", valueLabel: "species" }, { id: "cumulative", label: "Cumulative total", valueAggregation: "latest", valueColumn: "cumulative_species_count", valueLabel: "species" }], seriesColumn: "project_alias", seriesLabels: { abs: "ABS", aggregated: "Aggregated", obs: "OBS" }, seriesOrder: ["abs", "obs", "aggregated"], type: "time-series", valueColumn: "species_count", valueLabel: "species" } },
  createFocalTaxaReport({ ariaLabel: "Observations of OSA's focal amphibian and reptile species by project", dataSetOrder: ["23702", "21121", "21214", "30844", "31049"], fileName: "abs-vs-obs-key-amphibian-and-reptile-observations-over-time.csv", id: "focal-amphibians-and-reptiles-over-time", label: "Focal amphibians and reptiles over time" }),
  createFocalTaxaReport({ ariaLabel: "Observations of OSA's focal bird species by project", dataSetOrder: ["14308", "10126", "367618", "8479", "20856"], fileName: "abs-vs-obs-key-bird-observations-over-time.csv", id: "focal-birds-over-time", label: "Focal birds over time" }),
  createFocalTaxaReport({ ariaLabel: "Observations of OSA's focal marine taxa by project", dataSetLabel: "Taxon", dataSetOrder: ["41566", "39672", "41482", "776566", "516508"], fileName: "abs-vs-obs-key-marine-observations-over-time.csv", id: "focal-marine-life-over-time", label: "Focal marine life over time" }),
  createFocalTaxaReport({ ariaLabel: "Observations of OSA's focal mammal species by project", dataSetOrder: ["42007", "43411", "43355", "41970", "42115"], fileName: "abs-vs-obs-key-mammal-observations-over-time.csv", id: "focal-mammals-over-time", label: "Focal mammals over time" }),
  createFocalTaxaReport({ ariaLabel: "Observations of OSA's focal tree species by project", dataSetOrder: ["190315", "189310", "185878", "910767", "440806"], fileName: "abs-vs-obs-key-tree-observations-over-time.csv", id: "focal-trees-over-time", label: "Focal trees over time" }),
];

export const OSA_STATS_DATA_FILES = [
  ...OSA_STATS_REPORTS.map(({ fileName, id, label }) => ({ fileName, id, label })),
  ...OSA_STATS_REPORTS.flatMap((report) => report.relatedDownloads ?? []),
];
