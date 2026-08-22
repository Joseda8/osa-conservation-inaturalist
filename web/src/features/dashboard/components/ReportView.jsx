import DownloadCsvButton from "../../../components/actions/DownloadCsvButton";
import DataTable from "../../../components/visualizations/DataTable";
import PieChart from "../../../components/visualizations/PieChart";
import { getPieChartSlices, parseCsv } from "../utils/csv";

export default function ReportView({ csvContent, report }) {
  const [columns, ...rows] = parseCsv(csvContent);
  const pieChartSlices = report.visualization?.type === "pie" ? getPieChartSlices(csvContent, report.visualization.categoryColumn, report.visualization.valueColumn) : null;

  return (
    <>
      <div className="report-heading"><h3>{report.label}</h3><DownloadCsvButton csvContent={csvContent} fileName={report.fileName} /></div>
      {pieChartSlices ? <PieChart ariaLabel={report.visualization.ariaLabel} slices={pieChartSlices} totalLabel={report.visualization.totalLabel} valueLabel={report.visualization.valueLabel} /> : <DataTable columns={columns ?? []} rows={rows} />}
    </>
  );
}
