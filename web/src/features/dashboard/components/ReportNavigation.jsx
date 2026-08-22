import { useState } from "react";

export default function ReportNavigation({ activeReportId, reports, setActiveReportId }) {
  const [searchTerm, setSearchTerm] = useState("");
  const normalizedSearchTerm = searchTerm.trim().toLocaleLowerCase();
  const matchingReports = reports.filter((report) => report.label.toLocaleLowerCase().includes(normalizedSearchTerm));

  return (
    <div className="sidebar-report-navigation">
      <label className="visually-hidden" htmlFor="report-search">Search OSA statistics reports</label>
      <input className="report-search" id="report-search" onChange={(event) => setSearchTerm(event.target.value)} placeholder="Search tabs" type="search" value={searchTerm} />
      <nav aria-label="OSA statistics reports">
        {matchingReports.map((report) => <button aria-current={report.id === activeReportId ? "page" : undefined} className={report.id === activeReportId ? "sidebar-report-navigation-item active" : "sidebar-report-navigation-item"} key={report.id} onClick={() => setActiveReportId(report.id)} type="button">{report.label}</button>)}
        {matchingReports.length === 0 && <p className="report-search-empty">No matching tabs.</p>}
      </nav>
    </div>
  );
}
