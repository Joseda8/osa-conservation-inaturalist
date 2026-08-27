import { useState } from "react";

import SeriesSelector from "./SeriesSelector";

export default function GroupedBarChart({ ariaLabel, categories, series, total = null, totalLabel, totalSeriesId = null, valueLabel }) {
  const [activeBar, setActiveBar] = useState(null);
  const [selectedSeriesIds, setSelectedSeriesIds] = useState(() => series.map((seriesItem) => seriesItem.id));
  const visibleSeries = series.map((seriesItem, seriesIndex) => ({ ...seriesItem, seriesIndex })).filter((seriesItem) => selectedSeriesIds.includes(seriesItem.id));
  const maximumValue = Math.max(...categories.flatMap((category) => visibleSeries.map((seriesItem) => category.bars[seriesItem.seriesIndex].value)), 0);
  const selectedBar = activeBar === null ? null : { category: categories[activeBar.categoryIndex], series: visibleSeries.find((seriesItem) => seriesItem.id === activeBar.seriesId) };

  if (maximumValue === 0) {
    return <p className="empty-state">This report has no values.</p>;
  }

  function toggleSeries(seriesId) {
    setSelectedSeriesIds((currentSeriesIds) => currentSeriesIds.includes(seriesId) ? currentSeriesIds.filter((currentSeriesId) => currentSeriesId !== seriesId) : [...currentSeriesIds, seriesId]);
    setActiveBar(null);
  }

  return (
    <section aria-label={ariaLabel} className="grouped-bar-chart">
      <SeriesSelector items={series} onToggle={toggleSeries} selectedItemIds={selectedSeriesIds} />
      <div className="grouped-bar-chart-plot">
        <div className="bar-chart-totals">{total !== null && (totalSeriesId === null || selectedSeriesIds.includes(totalSeriesId)) && <span className="bar-chart-total"><span>{totalLabel}</span><strong>{total.toLocaleString()}</strong></span>}{visibleSeries.filter((seriesItem) => seriesItem.total !== null).map((seriesItem) => <span key={seriesItem.label}><span className="legend-swatch" style={{ backgroundColor: seriesItem.color }} />{seriesItem.label} total: <strong>{seriesItem.total.toLocaleString()}</strong></span>)}</div>
        <div className="grouped-bar-chart-bars">{categories.map((category, categoryIndex) => <div className="bar-group" key={category.label}><div className="bar-group-bars">{visibleSeries.map((seriesItem) => {
          const bar = category.bars[seriesItem.seriesIndex];
          const height = `${(bar.value / maximumValue) * 100}%`;
          return <div className="bar-column" key={seriesItem.id}>{bar.annotation !== null && <span className="bar-annotation">{bar.annotation.toFixed(1)}%</span>}<button aria-label={`${category.label}, ${seriesItem.label}: ${bar.value.toLocaleString()} ${valueLabel}${bar.annotation === null ? "" : `; ${bar.annotation.toFixed(1)}% of ${seriesItem.label} ${valueLabel}`}`} className={activeBar?.categoryIndex === categoryIndex && activeBar?.seriesId === seriesItem.id ? "bar active" : "bar"} onBlur={() => setActiveBar(null)} onFocus={() => setActiveBar({ categoryIndex, seriesId: seriesItem.id })} onMouseEnter={() => setActiveBar({ categoryIndex, seriesId: seriesItem.id })} onMouseLeave={() => setActiveBar(null)} style={{ "--bar-color": seriesItem.color, "--bar-height": height }} type="button"><span className="visually-hidden">{seriesItem.label}: {bar.value.toLocaleString()} {valueLabel}</span></button></div>;
        })}</div><strong className="bar-group-label">{category.label}</strong></div>)}</div>
      </div>
      <div className="grouped-bar-chart-details">
        <p className="chart-hint">Hover or focus a bar for its exact count.</p>
        {selectedBar && <div className="chart-tooltip"><strong>{selectedBar.category.label} · {selectedBar.series.label}</strong><span>{selectedBar.category.bars[selectedBar.series.seriesIndex].value.toLocaleString()} {valueLabel}</span>{selectedBar.category.bars[selectedBar.series.seriesIndex].annotation !== null && <span>{selectedBar.category.bars[selectedBar.series.seriesIndex].annotation.toFixed(1)}% of {selectedBar.series.label} {valueLabel}</span>}</div>}
        <ul className="chart-legend">{visibleSeries.map((seriesItem) => <li key={seriesItem.label}><span className="legend-swatch" style={{ backgroundColor: seriesItem.color }} /><span>{seriesItem.label}</span></li>)}</ul>
      </div>
    </section>
  );
}
