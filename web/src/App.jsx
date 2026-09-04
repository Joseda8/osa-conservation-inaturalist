import { useState } from "react";

import DashboardSidebar from "./features/dashboard/components/DashboardSidebar";
import ReportView from "./features/dashboard/components/ReportView";
import { DASHBOARD_DATA_FILES, DASHBOARD_REPORT_CATEGORIES, DASHBOARD_REPORTS, DASHBOARD_SECTIONS } from "./features/dashboard/config";
import { useDashboardReports } from "./features/dashboard/hooks/useDashboardReports";

export default function App() {
  const [activeSectionId, setActiveSectionId] = useState("osa-stats");
  const [activeReportId, setActiveReportId] = useState("observation-counts");
  const { errorMessage, reportContents } = useDashboardReports(DASHBOARD_DATA_FILES);
  const activeSection = DASHBOARD_SECTIONS.find((section) => section.id === activeSectionId);
  const activeReport = DASHBOARD_REPORTS.find((report) => report.id === activeReportId);

  return (
    <div className="dashboard-layout">
      <DashboardSidebar activeReportId={activeReportId} activeSectionId={activeSectionId} reportCategories={DASHBOARD_REPORT_CATEGORIES} reports={DASHBOARD_REPORTS} sections={DASHBOARD_SECTIONS} setActiveReportId={setActiveReportId} setActiveSectionId={setActiveSectionId} />
      <main className="content">
        <p className="eyebrow">Dashboard</p>
        <h2>{activeSection.label}</h2>
        <p className="section-description">{activeSection.description}</p>
        {errorMessage && <p className="error-state">{errorMessage} Run the Refresh GitHub Pages workflow to generate it.</p>}
        {reportContents === null && errorMessage === null && <p className="empty-state">Loading reports…</p>}
        {reportContents !== null && activeReport?.sectionId === activeSectionId && <ReportView csvContents={reportContents} report={activeReport} />}
      </main>
    </div>
  );
}
