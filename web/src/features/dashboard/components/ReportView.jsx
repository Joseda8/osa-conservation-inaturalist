import DownloadCsvButton from "../../../components/actions/DownloadCsvButton";
import DataTable from "../../../components/visualizations/DataTable";
import PieChart from "../../../components/visualizations/PieChart";
import { getCsvValue, getPieChartSlices, parseCsv } from "../utils/csv";

export default function ReportView({ csvContents, report }) {
  const csvContent = csvContents[report.id];
  const [columns, ...rows] = parseCsv(csvContent);
  const pieChartSlices = report.visualization?.type === "pie" ? getPieChartSlices(csvContent, report.visualization.categoryColumn, report.visualization.valueColumn, report.visualization.categoryLabels) : null;
  const summaryItems = report.visualization?.summaryItems?.map((summaryItem) => ({ ...summaryItem, value: getCsvValue(csvContents[summaryItem.sourceId], summaryItem.valueColumn) })) ?? [];
  const downloads = [{ csvContent, fileName: report.fileName, label: "Download CSV" }, ...(report.relatedDownloads ?? []).map((download) => ({ ...download, csvContent: csvContents[download.id] }))];

  return (
    <>
      <div className="report-heading"><h3>{report.label}</h3><div className="report-downloads">{downloads.map((download) => <DownloadCsvButton csvContent={download.csvContent} fileName={download.fileName} key={download.fileName} label={download.label} />)}</div></div>
      {pieChartSlices ? <PieChart ariaLabel={report.visualization.ariaLabel} slices={pieChartSlices} summaryItems={summaryItems} totalLabel={report.visualization.totalLabel} valueLabel={report.visualization.valueLabel} /> : <DataTable columns={columns ?? []} rows={rows} />}
    </>
  );
}
