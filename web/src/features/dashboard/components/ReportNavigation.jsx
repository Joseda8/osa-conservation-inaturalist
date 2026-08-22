export default function ReportNavigation({ activeReportId, reports, setActiveReportId }) {
  return (
    <nav aria-label="Section reports" className="sidebar-report-navigation">
      {reports.map((report) => <button aria-current={report.id === activeReportId ? "page" : undefined} className={report.id === activeReportId ? "sidebar-report-navigation-item active" : "sidebar-report-navigation-item"} key={report.id} onClick={() => setActiveReportId(report.id)} type="button">{report.label}</button>)}
    </nav>
  );
}
