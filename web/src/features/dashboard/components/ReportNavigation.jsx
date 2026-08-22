export default function ReportNavigation({ activeReportId, reports, setActiveReportId }) {
  return (
    <nav aria-label="OSA statistics reports" className="report-navigation">
      {reports.map((report) => <button aria-current={report.id === activeReportId ? "page" : undefined} className={report.id === activeReportId ? "report-navigation-item active" : "report-navigation-item"} key={report.id} onClick={() => setActiveReportId(report.id)} type="button">{report.label}</button>)}
    </nav>
  );
}
