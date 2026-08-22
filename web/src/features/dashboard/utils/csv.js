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

export function getPieChartSlices(csvContent, categoryColumn, valueColumn, categoryLabels = {}) {
  const [headerRow, ...dataRows] = parseCsv(csvContent);
  const categoryColumnIndex = headerRow.indexOf(categoryColumn);
  const valueColumnIndex = headerRow.indexOf(valueColumn);
  return dataRows.map((dataRow) => {
    const category = dataRow[categoryColumnIndex];
    return { count: Number(dataRow[valueColumnIndex]), label: categoryLabels[category] ?? category };
  });
}

export function getCsvValue(csvContent, valueColumn) {
  const [headerRow, firstDataRow] = parseCsv(csvContent);
  if (!headerRow || !firstDataRow) {
    return 0;
  }
  const value = Number(firstDataRow[headerRow.indexOf(valueColumn)]);
  return Number.isFinite(value) ? value : 0;
}

export function getGroupedBarChartData(csvContent, categoryColumn, seriesColumn, valueColumn, categoryLabels = {}, seriesLabels = {}) {
  const [headerRow, ...dataRows] = parseCsv(csvContent);
  const categoryColumnIndex = headerRow.indexOf(categoryColumn);
  const seriesColumnIndex = headerRow.indexOf(seriesColumn);
  const valueColumnIndex = headerRow.indexOf(valueColumn);
  const valuesByCategoryAndSeries = new Map();
  const seriesKeys = [];

  dataRows.forEach((dataRow) => {
    const category = dataRow[categoryColumnIndex];
    const series = dataRow[seriesColumnIndex];
    if (!valuesByCategoryAndSeries.has(category)) {
      valuesByCategoryAndSeries.set(category, new Map());
    }
    valuesByCategoryAndSeries.get(category).set(series, Number(dataRow[valueColumnIndex]) || 0);
    if (!seriesKeys.includes(series)) {
      seriesKeys.push(series);
    }
  });

  return {
    categories: [...valuesByCategoryAndSeries].map(([category, valuesBySeries]) => ({ label: categoryLabels[category] ?? category, values: seriesKeys.map((series) => valuesBySeries.get(series) ?? 0) })),
    series: seriesKeys.map((series, seriesIndex) => ({ color: `var(--bar-color-${seriesIndex + 1})`, label: seriesLabels[series] ?? series })),
  };
}

export function getTimeSeriesData(csvContent, dateColumn, seriesColumn, valueColumn, seriesLabels = {}) {
  const [headerRow, ...dataRows] = parseCsv(csvContent);
  const dateColumnIndex = headerRow.indexOf(dateColumn);
  const seriesColumnIndex = headerRow.indexOf(seriesColumn);
  const valueColumnIndex = headerRow.indexOf(valueColumn);
  const seriesKeys = [];
  const records = dataRows.map((dataRow) => {
    const series = dataRow[seriesColumnIndex];
    if (!seriesKeys.includes(series)) {
      seriesKeys.push(series);
    }
    return { date: dataRow[dateColumnIndex], series, value: Number(dataRow[valueColumnIndex]) || 0 };
  });

  return { records, series: seriesKeys.map((series, seriesIndex) => ({ color: `var(--bar-color-${seriesIndex + 1})`, id: series, label: seriesLabels[series] ?? series })) };
}
