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
  const [csvContent, setCsvContent] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const activeSection = DASHBOARD_SECTIONS.find((section) => section.id === activeSectionId);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/observations.csv`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("The observations CSV could not be loaded.");
        }
        return response.text();
      })
      .then(setCsvContent)
      .catch((error) => setErrorMessage(error.message));
  }, []);

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <p className="organization-name">OSA Conservation</p>
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
        {csvContent === null && errorMessage === null && <p className="empty-state">Loading observations…</p>}
        {csvContent !== null && <CsvTable csvContent={csvContent} />}
      </main>
    </div>
  );
}
