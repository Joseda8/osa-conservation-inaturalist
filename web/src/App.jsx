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

function DownloadCsvButton({ csvContent, fileName }) {
  function downloadCsv() {
    const downloadUrl = URL.createObjectURL(new Blob([csvContent], { type: "text/csv;charset=utf-8" }));
    const downloadLink = document.createElement("a");
    downloadLink.href = downloadUrl;
    downloadLink.download = fileName;
    downloadLink.click();
    URL.revokeObjectURL(downloadUrl);
  }

  return <button className="download-button" onClick={downloadCsv} type="button">Download CSV</button>;
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

function PieChart({ csvContent }) {
  const [headerRow, ...dataRows] = parseCsv(csvContent);
  const [hoveredSliceIndex, setHoveredSliceIndex] = useState(null);
  const projectAliasIndex = headerRow.indexOf("project_alias");
  const observationCountIndex = headerRow.indexOf("observation_count");
  const slices = dataRows.map((dataRow, rowIndex) => ({ count: Number(dataRow[observationCountIndex]), label: dataRow[projectAliasIndex].toUpperCase(), rowIndex }));
  const totalObservationCount = slices.reduce((total, slice) => total + slice.count, 0);
  const activeSlice = hoveredSliceIndex === null ? null : slices[hoveredSliceIndex];
  let startAngle = -90;

  if (totalObservationCount === 0) {
    return <p className="empty-state">This report has no observations.</p>;
  }

  function getPoint(angle) {
    const radians = (angle * Math.PI) / 180;
    return { x: 50 + 40 * Math.cos(radians), y: 50 + 40 * Math.sin(radians) };
  }

  return (
    <div className="pie-chart-layout">
      <div className="pie-chart" role="img" aria-label="Pie chart of observations per project">
        <svg viewBox="0 0 100 100">
          {slices.map((slice, sliceIndex) => {
            const endAngle = startAngle + (slice.count / totalObservationCount) * 360;
            const startPoint = getPoint(startAngle);
            const endPoint = getPoint(endAngle);
            const largeArcFlag = endAngle - startAngle > 180 ? 1 : 0;
            const path = `M 50 50 L ${startPoint.x} ${startPoint.y} A 40 40 0 ${largeArcFlag} 1 ${endPoint.x} ${endPoint.y} Z`;
            startAngle = endAngle;
            return <path aria-label={`${slice.label}: ${slice.count.toLocaleString()} observations`} className={sliceIndex === hoveredSliceIndex ? "pie-slice active" : "pie-slice"} d={path} fill={`var(--pie-color-${sliceIndex + 1})`} key={slice.label} onBlur={() => setHoveredSliceIndex(null)} onFocus={() => setHoveredSliceIndex(sliceIndex)} onMouseEnter={() => setHoveredSliceIndex(sliceIndex)} onMouseLeave={() => setHoveredSliceIndex(null)} tabIndex="0" />;
          })}
        </svg>
        <div className="pie-chart-total"><strong>{totalObservationCount.toLocaleString()}</strong><span>observations</span></div>
      </div>
      <div className="pie-chart-details">
        <p className="chart-hint">Hover or focus a slice for its exact count.</p>
        {activeSlice && <div className="chart-tooltip"><strong>{activeSlice.label}</strong><span>{activeSlice.count.toLocaleString()} observations</span><span>{((activeSlice.count / totalObservationCount) * 100).toFixed(1)}%</span></div>}
        <ul className="chart-legend">
          {slices.map((slice, sliceIndex) => <li key={slice.label}><span className="legend-swatch" style={{ backgroundColor: `var(--pie-color-${sliceIndex + 1})` }} /><span>{slice.label}</span><strong>{((slice.count / totalObservationCount) * 100).toFixed(1)}%</strong></li>)}
        </ul>
      </div>
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
            <div className="report-heading"><h3>{activeReport.label}</h3><DownloadCsvButton csvContent={reportContents[activeReport.id]} fileName={activeReport.fileName} /></div>
            {activeReport.id === "observation-counts" ? <PieChart csvContent={reportContents[activeReport.id]} /> : <CsvTable csvContent={reportContents[activeReport.id]} />}
          </>
        )}
      </main>
    </div>
  );
}
