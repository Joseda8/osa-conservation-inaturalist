import { useState } from "react";

import ReportNavigation from "./ReportNavigation";

export default function DashboardSidebar({ activeReportId, activeSectionId, reportCategories, reports, sections, setActiveReportId, setActiveSectionId }) {
  const [searchTerm, setSearchTerm] = useState("");
  const normalizedSearchTerm = searchTerm.trim().toLocaleLowerCase();
  const matchingSections = sections.filter((section) => section.label.toLocaleLowerCase().includes(normalizedSearchTerm));
  const matchingReports = reports.filter((report) => {
    const parentSection = sections.find((section) => section.id === report.sectionId);
    const parentCategory = reportCategories.find((category) => category.id === report.categoryId);
    return `${parentSection?.label} ${parentCategory?.label ?? ""} ${report.label}`.toLocaleLowerCase().includes(normalizedSearchTerm);
  });

  function selectSection(sectionId) {
    setActiveSectionId(sectionId);
    setActiveReportId(reports.find((report) => report.sectionId === sectionId)?.id ?? null);
    setSearchTerm("");
  }

  function selectReport(report) {
    setActiveSectionId(report.sectionId);
    setActiveReportId(report.id);
    setSearchTerm("");
  }

  return (
    <aside className="sidebar">
      <img alt="OSA Conservation: conserving Costa Rica's natural treasure" className="organization-logo" src={`${import.meta.env.BASE_URL}assets/osa-conservation-logo.png`} />
      <h1>iNaturalist dashboard</h1>
      <label className="visually-hidden" htmlFor="tab-search">Search dashboard tabs</label>
      <input className="tab-search" id="tab-search" onChange={(event) => setSearchTerm(event.target.value)} placeholder="Search tabs" type="search" value={searchTerm} />
      {normalizedSearchTerm ? <nav aria-label="Matching dashboard tabs" className="sidebar-search-results">{matchingSections.map((section) => <button className="navigation-item" key={section.id} onClick={() => selectSection(section.id)} type="button">{section.label}</button>)}{matchingReports.map((report) => <button className="sidebar-report-navigation-item" key={report.id} onClick={() => selectReport(report)} type="button">{sections.find((section) => section.id === report.sectionId)?.label}: {report.label}</button>)}{matchingSections.length + matchingReports.length === 0 && <p className="tab-search-empty">No matching tabs.</p>}</nav> : <div className="sidebar-navigation">{sections.map((section) => <div className="sidebar-navigation-section" key={section.id}><button aria-current={section.id === activeSectionId ? "page" : undefined} className={section.id === activeSectionId ? "navigation-item active" : "navigation-item"} onClick={() => selectSection(section.id)} type="button">{section.label}</button>{activeSectionId === section.id && reports.some((report) => report.sectionId === section.id) && <ReportNavigation activeReportId={activeReportId} categories={reportCategories.filter((category) => category.sectionId === section.id)} reports={reports.filter((report) => report.sectionId === section.id)} setActiveReportId={setActiveReportId} />}</div>)}</div>}
    </aside>
  );
}
