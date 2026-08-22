import { useEffect, useState } from "react";

const DASHBOARD_SECTIONS = [
  {
    description: "Observations from OSA Conservation projects.",
    id: "osa-stats",
    label: "OSA stats",
  },
  {
    description: "Observation trends across Costa Rica.",
    id: "national-trends",
    label: "National trends",
  },
];

const OSA_STATS_REPORTS = [
  { fileName: "abs-vs-obs-observation-counts.csv", id: "observation-counts", label: "Observations per project" },
  { fileName: "abs-vs-obs-observations-by-day.csv", id: "observations-by-day", label: "Observations per day" },
  { fileName: "abs-vs-obs-duplicate-observations.csv", id: "duplicate-observations", label: "Duplicate observations" },
  { fileName: "abs-vs-obs-quality-grades.csv", id: "quality-grades", label: "Quality grades" },
];

function parseCsv(csvContent) {
  const rows = [];
  let cell = "";
  let row = [];
  let insideQuotes = false;

  for (let characterIndex = 0; characterIndex < csvContent.length; characterIndex += 1) {
    const character = csvContent[characterIndex];
    const nextCharacter = csvContent[characterIndex + 1];
    if (character === '"' && insideQuotes && nextCharacter === '"') {
      cell += '"';
      characterIndex += 1;
    } else if (character === '"') {
      insideQuotes = !insideQuotes;
    } else if (character === "," && !insideQuotes) {
      row.push(cell);
      cell = "";
    } else if ((character === "\n" || character === "\r") && !insideQuotes) {
      if (character === "\r" && nextCharacter === "\n") {
        characterIndex += 1;
      }
      row.push(cell);
      if (row.some((value) => value !== "")) {
        rows.push(row);
      }
      row = [];
      cell = "";
    } else {
      cell += character;
    }
  }

  row.push(cell);
  if (row.some((value) => value !== "")) {
    rows.push(row);
  }
  return rows;
}

function CsvTable({ csvContent }) {
  const [headerRow, ...dataRows] = parseCsv(csvContent);
  if (!headerRow) {
    return <p className="empty-state">The CSV file has no rows.</p>;
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            {headerRow.map((column) => <th key={column}>{column}</th>)}
          </tr>
        </thead>
        <tbody>
          {dataRows.map((dataRow, rowIndex) => (
            <tr key={`${dataRow.join("-")}-${rowIndex}`}>
              {headerRow.map((column, columnIndex) => <td key={`${column}-${rowIndex}`}>{dataRow[columnIndex] ?? ""}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function App() {
  const [activeSectionId, setActiveSectionId] = useState(DASHBOARD_SECTIONS[0].id);
  const [activeReportId, setActiveReportId] = useState(OSA_STATS_REPORTS[0].id);
  const [reportContents, setReportContents] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const activeSection = DASHBOARD_SECTIONS.find((section) => section.id === activeSectionId);
  const activeReport = OSA_STATS_REPORTS.find((report) => report.id === activeReportId);

  useEffect(() => {
    Promise.all(OSA_STATS_REPORTS.map((report) => fetch(`${import.meta.env.BASE_URL}data/${report.fileName}`).then((response) => {
      if (!response.ok) {
        throw new Error(`The ${report.label.toLowerCase()} report could not be loaded.`);
      }
      return response.text();
    })))
      .then((csvContents) => setReportContents(Object.fromEntries(OSA_STATS_REPORTS.map((report, reportIndex) => [report.id, csvContents[reportIndex]]))))
      .catch((error) => setErrorMessage(error.message));
  }, []);

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <img alt="OSA Conservation: conserving Costa Rica's natural treasure" className="organization-logo" src={`${import.meta.env.BASE_URL}assets/osa-conservation-logo.png`} />
        <h1>iNaturalist dashboard</h1>
        <nav aria-label="Dashboard sections">
          {DASHBOARD_SECTIONS.map((section) => (
            <button aria-current={section.id === activeSectionId ? "page" : undefined} className={section.id === activeSectionId ? "navigation-item active" : "navigation-item"} key={section.id} onClick={() => setActiveSectionId(section.id)} type="button">
              {section.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="content">
        <p className="eyebrow">Dashboard</p>
        <h2>{activeSection.label}</h2>
        <p className="section-description">{activeSection.description}</p>
        {errorMessage && <p className="error-state">{errorMessage} Run the Refresh GitHub Pages workflow to generate it.</p>}
        {reportContents === null && errorMessage === null && <p className="empty-state">Loading reports…</p>}
        {activeSectionId === "national-trends" && <p className="empty-state">National trends will be added next.</p>}
        {activeSectionId === "osa-stats" && reportContents !== null && (
          <>
            <nav aria-label="OSA statistics reports" className="report-navigation">
              {OSA_STATS_REPORTS.map((report) => (
                <button aria-current={report.id === activeReportId ? "page" : undefined} className={report.id === activeReportId ? "report-navigation-item active" : "report-navigation-item"} key={report.id} onClick={() => setActiveReportId(report.id)} type="button">
                  {report.label}
                </button>
              ))}
            </nav>
            <h3>{activeReport.label}</h3>
            <CsvTable csvContent={reportContents[activeReport.id]} />
          </>
        )}
      </main>
    </div>
  );
}
