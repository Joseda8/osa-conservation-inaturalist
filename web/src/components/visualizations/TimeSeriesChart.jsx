import { useMemo, useState } from "react";

const CHART_HEIGHT = 320;
const CHART_PADDING = { bottom: 48, left: 54, right: 18, top: 18 };

// Radius of the selected data-point marker in SVG units.
const ACTIVE_POINT_RADIUS = 5;
const DEFAULT_RANGE_DAYS = 7;
const RANGE_PRESETS = [{ days: 7, id: "last-7", label: "Last 7 days" }, { days: 30, id: "last-30", label: "Last 30 days" }, { days: 90, id: "last-90", label: "Last 90 days" }, { id: "all", label: "All time" }];
const TIME_GROUPS = [{ id: "day", label: "Day" }, { id: "week", label: "Week" }, { id: "month", label: "Month" }, { id: "year", label: "Year" }];
const VISIBLE_X_AXIS_LABEL_COUNT = 6;
const Y_AXIS_LINE_COUNT = 4;

function addDays(date, days) {
  const result = new Date(`${date}T00:00:00Z`);
  result.setUTCDate(result.getUTCDate() + days);
  return result.toISOString().slice(0, 10);
}

function getWeekStart(date) {
  const result = new Date(`${date}T00:00:00Z`);
  const weekday = result.getUTCDay() || 7;
  result.setUTCDate(result.getUTCDate() - weekday + 1);
  return result.toISOString().slice(0, 10);
}

function getPeriodKey(date, grouping) {
  if (grouping === "week") {
    return getWeekStart(date);
  }
  if (grouping === "month") {
    return date.slice(0, 7);
  }
  if (grouping === "year") {
    return date.slice(0, 4);
  }
  return date;
}

function getPeriodKeys(startDate, endDate, grouping) {
  const keys = [];
  let currentKey = getPeriodKey(startDate, grouping);
  const finalKey = getPeriodKey(endDate, grouping);

  while (currentKey <= finalKey) {
    keys.push(currentKey);
    if (grouping === "week") {
      currentKey = addDays(currentKey, 7);
    } else if (grouping === "month") {
      const [year, month] = currentKey.split("-").map(Number);
      currentKey = `${year + (month === 12 ? 1 : 0)}-${String(month === 12 ? 1 : month + 1).padStart(2, "0")}`;
    } else if (grouping === "year") {
      currentKey = String(Number(currentKey) + 1);
    } else {
      currentKey = addDays(currentKey, 1);
    }
  }
  return keys;
}

function formatPeriodLabel(periodKey, grouping) {
  if (grouping === "year") {
    return periodKey;
  }
  if (grouping === "month") {
    return new Intl.DateTimeFormat("en", { month: "short", year: "numeric", timeZone: "UTC" }).format(new Date(`${periodKey}-01T00:00:00Z`));
  }
  return new Intl.DateTimeFormat("en", { day: "numeric", month: "short", year: grouping === "week" ? "numeric" : undefined, timeZone: "UTC" }).format(new Date(`${periodKey}T00:00:00Z`));
}

function getTickIndexes(pointCount) {
  if (pointCount <= VISIBLE_X_AXIS_LABEL_COUNT) {
    return Array.from({ length: pointCount }, (_, index) => index);
  }
  return Array.from({ length: VISIBLE_X_AXIS_LABEL_COUNT }, (_, index) => Math.round((index * (pointCount - 1)) / (VISIBLE_X_AXIS_LABEL_COUNT - 1)));
}

export default function TimeSeriesChart({ ariaLabel, records, series, valueLabel }) {
  const dates = records.map((record) => record.date).sort();
  const earliestDate = dates[0];
  const latestDate = dates[dates.length - 1];
  const defaultLatestDate = latestDate ?? "1970-01-01";
  const [grouping, setGrouping] = useState("day");
  const [rangePreset, setRangePreset] = useState("last-7");
  const [startDate, setStartDate] = useState(() => addDays(defaultLatestDate, 1 - DEFAULT_RANGE_DAYS));
  const [endDate, setEndDate] = useState(defaultLatestDate);
  const [activePoint, setActivePoint] = useState(null);
  const chartWidth = 720;
  const plotWidth = chartWidth - CHART_PADDING.left - CHART_PADDING.right;
  const plotHeight = CHART_HEIGHT - CHART_PADDING.top - CHART_PADDING.bottom;

  const chartData = useMemo(() => {
    const periodKeys = getPeriodKeys(startDate, endDate, grouping);
    const valuesByPeriodAndSeries = new Map(periodKeys.map((periodKey) => [periodKey, new Map()]));
    records.filter((record) => record.date >= startDate && record.date <= endDate).forEach((record) => {
      const periodKey = getPeriodKey(record.date, grouping);
      const periodValues = valuesByPeriodAndSeries.get(periodKey);
      periodValues.set(record.series, (periodValues.get(record.series) ?? 0) + record.value);
    });
    return periodKeys.map((periodKey) => ({ label: formatPeriodLabel(periodKey, grouping), periodKey, values: series.map((seriesItem) => valuesByPeriodAndSeries.get(periodKey).get(seriesItem.id) ?? 0) }));
  }, [endDate, grouping, records, series, startDate]);

  const maximumValue = useMemo(() => Math.max(...chartData.flatMap((point) => point.values), 0), [chartData]);
  const scaleMaximumValue = Math.max(maximumValue, 1);
  const linePoints = useMemo(() => series.map((seriesItem, seriesIndex) => chartData.map((point, pointIndex) => {
    const x = chartData.length === 1 ? CHART_PADDING.left + plotWidth / 2 : CHART_PADDING.left + (pointIndex * plotWidth) / (chartData.length - 1);
    const y = CHART_PADDING.top + plotHeight - (point.values[seriesIndex] / scaleMaximumValue) * plotHeight;
    return `${x},${y}`;
  }).join(" ")), [chartData, plotHeight, plotWidth, scaleMaximumValue, series]);
  const selectedPoint = activePoint === null ? null : chartData[activePoint.pointIndex];

  if (!earliestDate || !latestDate) {
    return <p className="empty-state">This report has no values.</p>;
  }

  function selectRange(preset) {
    setRangePreset(preset.id);
    setEndDate(latestDate);
    setStartDate(preset.id === "all" ? earliestDate : addDays(latestDate, 1 - preset.days));
    setActivePoint(null);
  }

  function updateStartDate(value) {
    setRangePreset("custom");
    setStartDate(value);
    setActivePoint(null);
  }

  function updateEndDate(value) {
    setRangePreset("custom");
    setEndDate(value);
    setActivePoint(null);
  }

  function getPointX(pointIndex) {
    return chartData.length === 1 ? CHART_PADDING.left + plotWidth / 2 : CHART_PADDING.left + (pointIndex * plotWidth) / (chartData.length - 1);
  }

  function getPointY(pointIndex, seriesIndex) {
    return CHART_PADDING.top + plotHeight - (chartData[pointIndex].values[seriesIndex] / scaleMaximumValue) * plotHeight;
  }

  function selectPointByPointerPosition(clientX, clientY, chartElement) {
    const chartBounds = chartElement.getBoundingClientRect();
    const relativeX = ((clientX - chartBounds.left) / chartBounds.width) * chartWidth;
    const relativeY = ((clientY - chartBounds.top) / chartBounds.height) * CHART_HEIGHT;
    const pointIndex = chartData.length === 1 ? 0 : Math.max(0, Math.min(chartData.length - 1, Math.round(((relativeX - CHART_PADDING.left) * (chartData.length - 1)) / plotWidth)));
    const seriesIndex = chartData[pointIndex].values.reduce((closestSeriesIndex, value, candidateSeriesIndex) => Math.abs(CHART_PADDING.top + plotHeight - (value / scaleMaximumValue) * plotHeight - relativeY) < Math.abs(getPointY(pointIndex, closestSeriesIndex) - relativeY) ? candidateSeriesIndex : closestSeriesIndex, 0);
    setActivePoint((currentPoint) => currentPoint?.pointIndex === pointIndex && currentPoint.seriesIndex === seriesIndex ? currentPoint : { pointIndex, seriesIndex });
  }

  function selectPointByKeyboard(event) {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
      return;
    }
    event.preventDefault();
    const currentPoint = activePoint ?? { pointIndex: 0, seriesIndex: 0 };
    const pointIndex = Math.max(0, Math.min(chartData.length - 1, currentPoint.pointIndex + (event.key === "ArrowLeft" ? -1 : 1)));
    setActivePoint({ pointIndex, seriesIndex: currentPoint.seriesIndex });
  }

  if (startDate > endDate) {
    return <p className="empty-state">Choose an end date on or after the start date.</p>;
  }

  return (
    <section aria-label={ariaLabel} className="time-series-chart">
      <div className="time-series-controls">
        <div className="time-series-control-group"><span>Range</span><div className="time-series-button-group">{RANGE_PRESETS.map((preset) => <button aria-pressed={rangePreset === preset.id} className={rangePreset === preset.id ? "time-series-control active" : "time-series-control"} key={preset.id} onClick={() => selectRange(preset)} type="button">{preset.label}</button>)}</div></div>
        <div className="time-series-control-group"><span>Group by</span><div className="time-series-button-group">{TIME_GROUPS.map((timeGroup) => <button aria-pressed={grouping === timeGroup.id} className={grouping === timeGroup.id ? "time-series-control active" : "time-series-control"} key={timeGroup.id} onClick={() => { setGrouping(timeGroup.id); setActivePoint(null); }} type="button">{timeGroup.label}</button>)}</div></div>
        <div className="time-series-date-range"><label>From<input max={endDate} min={earliestDate} onChange={(event) => updateStartDate(event.target.value)} type="date" value={startDate} /></label><label>To<input max={latestDate} min={startDate} onChange={(event) => updateEndDate(event.target.value)} type="date" value={endDate} /></label></div>
      </div>
      <div className="time-series-plot-scroll"><div aria-label={`${ariaLabel}. Hover to inspect a date, or use the left and right arrow keys.`} className="time-series-plot" onFocus={() => setActivePoint((currentPoint) => currentPoint ?? { pointIndex: 0, seriesIndex: 0 })} onKeyDown={selectPointByKeyboard} onMouseLeave={() => setActivePoint(null)} onMouseMove={(event) => selectPointByPointerPosition(event.clientX, event.clientY, event.currentTarget)} role="group" tabIndex={0}><svg aria-hidden="true" viewBox={`0 0 ${chartWidth} ${CHART_HEIGHT}`}>{Array.from({ length: Y_AXIS_LINE_COUNT }, (_, lineIndex) => {
        const y = CHART_PADDING.top + (lineIndex * plotHeight) / (Y_AXIS_LINE_COUNT - 1);
        const value = Math.round(maximumValue - (lineIndex * maximumValue) / (Y_AXIS_LINE_COUNT - 1));
        return <g key={lineIndex}><line className="time-series-grid-line" x1={CHART_PADDING.left} x2={chartWidth - CHART_PADDING.right} y1={y} y2={y} /><text className="time-series-axis-label" textAnchor="end" x={CHART_PADDING.left - 8} y={y + 4}>{value.toLocaleString()}</text></g>;
      })}{series.map((seriesItem, seriesIndex) => <polyline className="time-series-line" key={seriesItem.id} points={linePoints[seriesIndex]} stroke={seriesItem.color} />)}{activePoint && <circle className="time-series-active-point" cx={getPointX(activePoint.pointIndex)} cy={getPointY(activePoint.pointIndex, activePoint.seriesIndex)} fill={series[activePoint.seriesIndex].color} r={ACTIVE_POINT_RADIUS} />}{getTickIndexes(chartData.length).map((pointIndex) => {
        const x = getPointX(pointIndex);
        return <text className="time-series-axis-label" key={chartData[pointIndex].periodKey} textAnchor="middle" x={x} y={CHART_HEIGHT - 14}>{chartData[pointIndex].label}</text>;
      })}</svg></div></div>
      <div className="time-series-details"><div><p className="chart-hint">Hover over the chart for an exact count, or use its arrow keys.</p>{selectedPoint && <div className="chart-tooltip"><strong>{selectedPoint.label} · {series[activePoint.seriesIndex].label}</strong><span>{selectedPoint.values[activePoint.seriesIndex].toLocaleString()} {valueLabel}</span></div>}</div><ul className="chart-legend">{series.map((seriesItem) => <li key={seriesItem.id}><span className="legend-swatch" style={{ backgroundColor: seriesItem.color }} /><span>{seriesItem.label}</span></li>)}</ul></div>
    </section>
  );
}
