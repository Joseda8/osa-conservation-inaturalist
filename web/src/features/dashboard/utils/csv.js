export function parseCsv(csvContent) {
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

export function getPieChartSlices(csvContent, categoryColumn, valueColumn) {
  const [headerRow, ...dataRows] = parseCsv(csvContent);
  const categoryColumnIndex = headerRow.indexOf(categoryColumn);
  const valueColumnIndex = headerRow.indexOf(valueColumn);
  return dataRows.map((dataRow) => ({ count: Number(dataRow[valueColumnIndex]), label: dataRow[categoryColumnIndex] }));
}
