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

export function getPieChartSlices(csvContent, categoryColumn, valueColumn, categoryLabels = {}, excludedCategories = [], detailColumn) {
  const [headerRow, ...dataRows] = parseCsv(csvContent);
  const categoryColumnIndex = headerRow.indexOf(categoryColumn);
  const valueColumnIndex = headerRow.indexOf(valueColumn);
  const detailColumnIndex = headerRow.indexOf(detailColumn);
  return dataRows.filter((dataRow) => !excludedCategories.includes(dataRow[categoryColumnIndex])).map((dataRow) => {
    const category = dataRow[categoryColumnIndex];
    const detail = Number(dataRow[detailColumnIndex]);
    return { count: Number(dataRow[valueColumnIndex]), detail: detailColumnIndex === -1 || !Number.isFinite(detail) ? null : detail, id: category, label: categoryLabels[category] ?? category };
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

export function getCsvValueForCategory(csvContent, categoryColumn, categoryValue, valueColumn) {
  const [headerRow, ...dataRows] = parseCsv(csvContent);
  const categoryColumnIndex = headerRow?.indexOf(categoryColumn) ?? -1;
  const valueColumnIndex = headerRow?.indexOf(valueColumn) ?? -1;
  const dataRow = dataRows.find((row) => row[categoryColumnIndex] === categoryValue);
  if (!dataRow || valueColumnIndex === -1) {
    return null;
  }
  const value = Number(dataRow[valueColumnIndex]);
  return Number.isFinite(value) ? value : null;
}

export function getOptionalCsvValue(csvContent, valueColumn) {
  const [headerRow, firstDataRow] = parseCsv(csvContent);
  const valueColumnIndex = headerRow?.indexOf(valueColumn) ?? -1;
  if (!firstDataRow || valueColumnIndex === -1) {
    return null;
  }
  const value = Number(firstDataRow[valueColumnIndex]);
  return Number.isFinite(value) ? value : null;
}

export function getGroupedBarChartData(csvContent, categoryColumn, seriesColumn, valueColumn, annotationColumn, totalColumn, categoryLabels = {}, seriesLabels = {}, excludedSeries = [], seriesOrder = [], hiddenTotalSeries = []) {
  const [headerRow, ...dataRows] = parseCsv(csvContent);
  const categoryColumnIndex = headerRow.indexOf(categoryColumn);
  const seriesColumnIndex = headerRow.indexOf(seriesColumn);
  const valueColumnIndex = headerRow.indexOf(valueColumn);
  const annotationColumnIndex = headerRow.indexOf(annotationColumn);
  const totalColumnIndex = headerRow.indexOf(totalColumn);
  const valuesByCategoryAndSeries = new Map();
  const seriesKeys = [];
  const totalsBySeries = new Map();

  dataRows.filter((dataRow) => !excludedSeries.includes(dataRow[seriesColumnIndex])).forEach((dataRow) => {
    const category = dataRow[categoryColumnIndex];
    const series = dataRow[seriesColumnIndex];
    if (!valuesByCategoryAndSeries.has(category)) {
      valuesByCategoryAndSeries.set(category, new Map());
    }
    valuesByCategoryAndSeries.get(category).set(series, { annotation: annotationColumnIndex === -1 ? null : Number(dataRow[annotationColumnIndex]) || 0, value: Number(dataRow[valueColumnIndex]) || 0 });
    if (!totalsBySeries.has(series)) {
      totalsBySeries.set(series, totalColumnIndex === -1 ? null : Number(dataRow[totalColumnIndex]) || 0);
    }
    if (!seriesKeys.includes(series)) {
      seriesKeys.push(series);
    }
  });

  const orderedSeriesKeys = [...seriesKeys].sort((firstSeries, secondSeries) => (seriesOrder.indexOf(firstSeries) === -1 ? seriesOrder.length : seriesOrder.indexOf(firstSeries)) - (seriesOrder.indexOf(secondSeries) === -1 ? seriesOrder.length : seriesOrder.indexOf(secondSeries)));
  return {
    categories: [...valuesByCategoryAndSeries].map(([category, valuesBySeries]) => ({ bars: orderedSeriesKeys.map((series) => valuesBySeries.get(series) ?? { annotation: null, value: 0 }), label: categoryLabels[category] ?? category })),
    series: orderedSeriesKeys.map((series, seriesIndex) => ({ color: `var(--bar-color-${seriesIndex + 1})`, id: series, label: seriesLabels[series] ?? series, total: hiddenTotalSeries.includes(series) ? null : totalsBySeries.get(series) })),
  };
}

export function getTimeSeriesData(csvContent, dateColumn, seriesColumn, valueColumn, seriesLabels = {}, excludedSeries = [], seriesOrder = []) {
  const [headerRow, ...dataRows] = parseCsv(csvContent);
  const dateColumnIndex = headerRow.indexOf(dateColumn);
  const seriesColumnIndex = headerRow.indexOf(seriesColumn);
  const valueColumnIndex = headerRow.indexOf(valueColumn);
  const seriesKeys = [];
  const records = dataRows.filter((dataRow) => !excludedSeries.includes(dataRow[seriesColumnIndex])).map((dataRow) => {
    const series = dataRow[seriesColumnIndex];
    if (!seriesKeys.includes(series)) {
      seriesKeys.push(series);
    }
    return { date: dataRow[dateColumnIndex], series, value: Number(dataRow[valueColumnIndex]) || 0 };
  });

  const orderedSeriesKeys = [...seriesKeys].sort((firstSeries, secondSeries) => (seriesOrder.indexOf(firstSeries) === -1 ? seriesOrder.length : seriesOrder.indexOf(firstSeries)) - (seriesOrder.indexOf(secondSeries) === -1 ? seriesOrder.length : seriesOrder.indexOf(secondSeries)));
  return { records, series: orderedSeriesKeys.map((series, seriesIndex) => ({ color: `var(--bar-color-${seriesIndex + 1})`, id: series, label: seriesLabels[series] ?? series })) };
}
