import { useState } from "react";

import DashboardSidebar from "./features/dashboard/components/DashboardSidebar";
import ReportView from "./features/dashboard/components/ReportView";
import { DASHBOARD_REPORT_CATEGORIES, DASHBOARD_SECTIONS, OSA_STATS_DATA_FILES, OSA_STATS_REPORTS } from "./features/dashboard/config";
import { useDashboardReports } from "./features/dashboard/hooks/useDashboardReports";

export default function App() {
  const [activeSectionId, setActiveSectionId] = useState("osa-stats");
  const [activeReportId, setActiveReportId] = useState("observation-counts");
  const { errorMessage, reportContents } = useDashboardReports(OSA_STATS_DATA_FILES);
  const activeSection = DASHBOARD_SECTIONS.find((section) => section.id === activeSectionId);
  const activeReport = OSA_STATS_REPORTS.find((report) => report.id === activeReportId);

  return (
    <div className="dashboard-layout">
      <DashboardSidebar activeReportId={activeReportId} activeSectionId={activeSectionId} reportCategories={DASHBOARD_REPORT_CATEGORIES} reports={OSA_STATS_REPORTS} sections={DASHBOARD_SECTIONS} setActiveReportId={setActiveReportId} setActiveSectionId={setActiveSectionId} />
      <main className="content">
        <p className="eyebrow">Dashboard</p>
        <h2>{activeSection.label}</h2>
        <p className="section-description">{activeSection.description}</p>
        {errorMessage && <p className="error-state">{errorMessage} Run the Refresh GitHub Pages workflow to generate it.</p>}
        {reportContents === null && errorMessage === null && <p className="empty-state">Loading reports…</p>}
        {activeSectionId === "national-trends" && <p className="empty-state">National trends will be added next.</p>}
        {activeSectionId === "osa-stats" && reportContents !== null && <ReportView csvContents={reportContents} report={activeReport} />}
      </main>
    </div>
  );
}
