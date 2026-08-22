import { useState } from "react";

export default function GroupedBarChart({ ariaLabel, categories, series, total = null, totalLabel, valueLabel }) {
  const [activeBar, setActiveBar] = useState(null);
  const maximumValue = Math.max(...categories.flatMap((category) => category.bars.map((bar) => bar.value)), 0);
  const selectedBar = activeBar === null ? null : { category: categories[activeBar.categoryIndex], series: series[activeBar.seriesIndex] };

  if (maximumValue === 0) {
    return <p className="empty-state">This report has no values.</p>;
  }

  return (
    <section aria-label={ariaLabel} className="grouped-bar-chart">
      <div className="grouped-bar-chart-plot">
        <div className="bar-chart-totals">{total !== null && <span className="bar-chart-total"><span>{totalLabel}</span><strong>{total.toLocaleString()}</strong></span>}{series.filter((seriesItem) => seriesItem.total !== null).map((seriesItem) => <span key={seriesItem.label}><span className="legend-swatch" style={{ backgroundColor: seriesItem.color }} />{seriesItem.label} total: <strong>{seriesItem.total.toLocaleString()}</strong></span>)}</div>
        <div className="grouped-bar-chart-bars">{categories.map((category, categoryIndex) => <div className="bar-group" key={category.label}><div className="bar-group-bars">{series.map((seriesItem, seriesIndex) => {
          const bar = category.bars[seriesIndex];
          const height = `${(bar.value / maximumValue) * 100}%`;
          return <div className="bar-column" key={seriesItem.label}>{bar.annotation !== null && <span className="bar-annotation">{bar.annotation.toFixed(1)}%</span>}<button aria-label={`${category.label}, ${seriesItem.label}: ${bar.value.toLocaleString()} ${valueLabel}${bar.annotation === null ? "" : `; ${bar.annotation.toFixed(1)}% of ${seriesItem.label} ${valueLabel}`}`} className={activeBar?.categoryIndex === categoryIndex && activeBar?.seriesIndex === seriesIndex ? "bar active" : "bar"} onBlur={() => setActiveBar(null)} onFocus={() => setActiveBar({ categoryIndex, seriesIndex })} onMouseEnter={() => setActiveBar({ categoryIndex, seriesIndex })} onMouseLeave={() => setActiveBar(null)} style={{ "--bar-color": seriesItem.color, "--bar-height": height }} type="button"><span className="visually-hidden">{seriesItem.label}: {bar.value.toLocaleString()} {valueLabel}</span></button></div>;
        })}</div><strong className="bar-group-label">{category.label}</strong></div>)}</div>
      </div>
      <div className="grouped-bar-chart-details">
        <p className="chart-hint">Hover or focus a bar for its exact count.</p>
        {selectedBar && <div className="chart-tooltip"><strong>{selectedBar.category.label} · {selectedBar.series.label}</strong><span>{selectedBar.category.bars[activeBar.seriesIndex].value.toLocaleString()} {valueLabel}</span>{selectedBar.category.bars[activeBar.seriesIndex].annotation !== null && <span>{selectedBar.category.bars[activeBar.seriesIndex].annotation.toFixed(1)}% of {selectedBar.series.label} {valueLabel}</span>}</div>}
        <ul className="chart-legend">{series.map((seriesItem) => <li key={seriesItem.label}><span className="legend-swatch" style={{ backgroundColor: seriesItem.color }} /><span>{seriesItem.label}</span></li>)}</ul>
      </div>
    </section>
  );
}
