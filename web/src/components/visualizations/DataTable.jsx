export default function DataTable({ columns, rows }) {
  if (columns.length === 0) {
    return <p className="empty-state">This report has no rows.</p>;
  }

  return (
    <div className="table-container">
      <table>
        <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
        <tbody>
          {rows.map((row, rowIndex) => <tr key={`${row.join("-")}-${rowIndex}`}>{columns.map((column, columnIndex) => <td key={`${column}-${rowIndex}`}>{row[columnIndex] ?? ""}</td>)}</tr>)}
        </tbody>
      </table>
    </div>
  );
}
