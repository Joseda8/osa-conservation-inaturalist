import DownloadCsvButton from "../../../components/actions/DownloadCsvButton";
import InfoTooltip from "../../../components/feedback/InfoTooltip";
import DataTable from "../../../components/visualizations/DataTable";
import GroupedBarChart from "../../../components/visualizations/GroupedBarChart";
import PieChart from "../../../components/visualizations/PieChart";
import RankedBarChart from "../../../components/visualizations/RankedBarChart";
import TimeSeriesChart from "../../../components/visualizations/TimeSeriesChart";
import { getCsvValue, getCsvValueForCategory, getGroupedBarChartData, getOptionalCsvValue, getPieChartSlices, getRankedBarChartData, getTimeSeriesData, getTimeSeriesDataSets, parseCsv } from "../utils/csv";

export default function ReportView({ csvContents, report }) {
  const csvContent = csvContents[report.id];
  const [columns, ...rows] = parseCsv(csvContent);
  const pieChartSlices = report.visualization?.type === "pie" ? getPieChartSlices(csvContent, report.visualization.categoryColumn, report.visualization.valueColumn, report.visualization.categoryLabels, report.visualization.excludedCategories) : null;
  const pieChartTotal = report.visualization?.totalCategory ? getCsvValueForCategory(csvContent, report.visualization.categoryColumn, report.visualization.totalCategory, report.visualization.valueColumn) : null;
  const groupedBarChartData = report.visualization?.type === "grouped-bar" ? getGroupedBarChartData(csvContent, report.visualization.categoryColumn, report.visualization.seriesColumn, report.visualization.valueColumn, report.visualization.annotationColumn, report.visualization.totalColumn, report.visualization.categoryLabels, report.visualization.seriesLabels, report.visualization.excludedSeries, report.visualization.seriesOrder, report.visualization.hiddenTotalSeries) : null;
  const rankedBarChartData = report.visualization?.type === "ranked-bar" ? getRankedBarChartData(csvContent, report.visualization.groupColumn, report.visualization.groupLabelColumn, report.visualization.itemColumn, report.visualization.itemDetailColumn, report.visualization.itemBadgeColumn, report.visualization.itemBadgeColors, report.visualization.itemAnnotationColumn, report.visualization.itemAnnotationTotalColumn, report.visualization.rankColumn, report.visualization.valueColumn, report.visualization.groupLabels, report.visualization.groupOrder) : null;
  const groupedBarChartTotal = report.visualization?.totalObservationColumn ? getOptionalCsvValue(csvContent, report.visualization.totalObservationColumn) : null;
  const timeSeriesData = report.visualization?.type === "time-series" ? getTimeSeriesData(csvContent, report.visualization.dateColumn, report.visualization.seriesColumn, report.visualization.valueColumn, report.visualization.seriesLabels, report.visualization.excludedSeries, report.visualization.seriesOrder) : null;
  const timeSeriesDataSets = report.visualization?.dataSetColumn ? getTimeSeriesDataSets(csvContent, report.visualization.dataSetColumn, report.visualization.dataSetLabelColumn, report.visualization.dateColumn, report.visualization.seriesColumn, report.visualization.valueColumn, report.visualization.seriesLabels, report.visualization.excludedSeries, report.visualization.seriesOrder, report.visualization.dataSetOrder) : [];
  const timeSeriesMeasures = report.visualization?.measures?.map((measure) => ({ ...measure, ...getTimeSeriesData(csvContent, report.visualization.dateColumn, report.visualization.seriesColumn, measure.valueColumn, report.visualization.seriesLabels, report.visualization.excludedSeries, report.visualization.seriesOrder) })) ?? [];
  const summaryItems = report.visualization?.summaryItems?.map((summaryItem) => ({ ...summaryItem, value: getCsvValue(csvContents[summaryItem.sourceId], summaryItem.valueColumn) })) ?? [];
  const downloads = [{ csvContent, fileName: report.fileName, label: "Download CSV" }, ...(report.relatedDownloads ?? []).map((download) => ({ ...download, csvContent: csvContents[download.id] }))];

  return (
    <>
      <div className="report-heading"><h3>{report.label}{report.infoText && <InfoTooltip label={`More information about ${report.label}`}>{report.infoText}</InfoTooltip>}</h3><div className="report-downloads">{downloads.map((download) => <DownloadCsvButton csvContent={download.csvContent} fileName={download.fileName} key={download.fileName} label={download.label} />)}</div></div>
      {pieChartSlices ? <PieChart ariaLabel={report.visualization.ariaLabel} slices={pieChartSlices} summaryItems={summaryItems} total={pieChartTotal} totalLabel={report.visualization.totalLabel} valueLabel={report.visualization.valueLabel} /> : groupedBarChartData ? <GroupedBarChart ariaLabel={report.visualization.ariaLabel} categories={groupedBarChartData.categories} series={groupedBarChartData.series} seriesSummaryLabel={report.visualization.seriesSummaryLabel} seriesSummaryValueLabel={report.visualization.seriesSummaryValueLabel} total={groupedBarChartTotal} totalLabel={report.visualization.totalLabel} totalSeriesId={report.visualization.totalSeriesId} valueLabel={report.visualization.valueLabel} /> : rankedBarChartData ? <RankedBarChart annotationLabel={report.visualization.itemAnnotationLabel} ariaLabel={report.visualization.ariaLabel} groups={rankedBarChartData} key={report.id} rankLimitOptions={report.visualization.rankLimitOptions} valueLabel={report.visualization.valueLabel} /> : timeSeriesData ? <TimeSeriesChart allowedGroupings={report.visualization.allowedGroupings} ariaLabel={report.visualization.ariaLabel} dataSetLabel={report.visualization.dataSetLabel} dataSets={timeSeriesDataSets} defaultGrouping={report.visualization.defaultGrouping} defaultRangePreset={report.visualization.defaultRangePreset} key={report.id} measures={timeSeriesMeasures} records={timeSeriesData.records} series={timeSeriesData.series} valueLabel={report.visualization.valueLabel} /> : <DataTable columns={columns ?? []} rows={rows} />}
    </>
  );
}
