import { useEffect, useState } from "react";

export default function ReportNavigation({ activeReportId, categories, reports, setActiveReportId }) {
  const ungroupedReports = reports.filter((report) => report.categoryId === undefined);
  const navigationItems = [...ungroupedReports.map((report) => ({ ...report, type: "report" })), ...categories.filter((category) => reports.some((report) => report.categoryId === category.id)).map((category) => ({ ...category, type: "category" }))].sort((firstItem, secondItem) => firstItem.label.localeCompare(secondItem.label));
  const activeCategoryId = reports.find((report) => report.id === activeReportId)?.categoryId;
  const [expandedCategoryIds, setExpandedCategoryIds] = useState(() => new Set(activeCategoryId ? [activeCategoryId] : []));

  useEffect(() => {
    if (activeCategoryId) {
      setExpandedCategoryIds((currentCategoryIds) => currentCategoryIds.has(activeCategoryId) ? currentCategoryIds : new Set([...currentCategoryIds, activeCategoryId]));
    }
  }, [activeCategoryId]);

  function toggleCategory(categoryId) {
    setExpandedCategoryIds((currentCategoryIds) => {
      const nextCategoryIds = new Set(currentCategoryIds);
      if (nextCategoryIds.has(categoryId)) {
        nextCategoryIds.delete(categoryId);
      } else {
        nextCategoryIds.add(categoryId);
      }
      return nextCategoryIds;
    });
  }

  return (
    <nav aria-label="Section reports" className="sidebar-report-navigation">
      {navigationItems.map((navigationItem) => navigationItem.type === "report" ? <button aria-current={navigationItem.id === activeReportId ? "page" : undefined} className={navigationItem.id === activeReportId ? "sidebar-report-navigation-item active" : "sidebar-report-navigation-item"} key={navigationItem.id} onClick={() => setActiveReportId(navigationItem.id)} type="button">{navigationItem.label}</button> : <div className="sidebar-report-category" key={navigationItem.id}><button aria-expanded={expandedCategoryIds.has(navigationItem.id)} className="sidebar-report-category-toggle" onClick={() => toggleCategory(navigationItem.id)} type="button"><span>{navigationItem.label}</span><span aria-hidden="true">{expandedCategoryIds.has(navigationItem.id) ? "▾" : "▸"}</span></button>{expandedCategoryIds.has(navigationItem.id) && reports.filter((report) => report.categoryId === navigationItem.id).sort((firstReport, secondReport) => firstReport.label.localeCompare(secondReport.label)).map((report) => <button aria-current={report.id === activeReportId ? "page" : undefined} className={report.id === activeReportId ? "sidebar-report-navigation-item active" : "sidebar-report-navigation-item"} key={report.id} onClick={() => setActiveReportId(report.id)} type="button">{report.label}</button>)}</div>)}
    </nav>
  );
}
