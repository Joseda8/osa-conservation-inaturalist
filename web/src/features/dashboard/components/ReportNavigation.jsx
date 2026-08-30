export default function ReportNavigation({ activeReportId, categories, reports, setActiveReportId }) {
  const ungroupedReports = reports.filter((report) => report.categoryId === undefined);
  const navigationItems = [...ungroupedReports.map((report) => ({ ...report, type: "report" })), ...categories.filter((category) => reports.some((report) => report.categoryId === category.id)).map((category) => ({ ...category, type: "category" }))].sort((firstItem, secondItem) => firstItem.label.localeCompare(secondItem.label));

  return (
    <nav aria-label="Section reports" className="sidebar-report-navigation">
      {navigationItems.map((navigationItem) => navigationItem.type === "report" ? <button aria-current={navigationItem.id === activeReportId ? "page" : undefined} className={navigationItem.id === activeReportId ? "sidebar-report-navigation-item active" : "sidebar-report-navigation-item"} key={navigationItem.id} onClick={() => setActiveReportId(navigationItem.id)} type="button">{navigationItem.label}</button> : <div className="sidebar-report-category" key={navigationItem.id}><span>{navigationItem.label}</span>{reports.filter((report) => report.categoryId === navigationItem.id).sort((firstReport, secondReport) => firstReport.label.localeCompare(secondReport.label)).map((report) => <button aria-current={report.id === activeReportId ? "page" : undefined} className={report.id === activeReportId ? "sidebar-report-navigation-item active" : "sidebar-report-navigation-item"} key={report.id} onClick={() => setActiveReportId(report.id)} type="button">{report.label}</button>)}</div>)}
    </nav>
  );
}
