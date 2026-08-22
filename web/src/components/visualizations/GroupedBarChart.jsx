import { useState } from "react";

export default function GroupedBarChart({ ariaLabel, categories, series, valueLabel }) {
  const [activeBar, setActiveBar] = useState(null);
  const maximumValue = Math.max(...categories.flatMap((category) => category.values), 0);
  const selectedBar = activeBar === null ? null : { category: categories[activeBar.categoryIndex], series: series[activeBar.seriesIndex] };

  if (maximumValue === 0) {
    return <p className="empty-state">This report has no values.</p>;
  }

  return (
    <section aria-label={ariaLabel} className="grouped-bar-chart">
      <div className="grouped-bar-chart-plot">
        {categories.map((category, categoryIndex) => <div className="bar-group" key={category.label}><div className="bar-group-bars">{series.map((seriesItem, seriesIndex) => {
          const value = category.values[seriesIndex];
          const height = `${(value / maximumValue) * 100}%`;
          return <button aria-label={`${category.label}, ${seriesItem.label}: ${value.toLocaleString()} ${valueLabel}`} className={activeBar?.categoryIndex === categoryIndex && activeBar?.seriesIndex === seriesIndex ? "bar active" : "bar"} key={seriesItem.label} onBlur={() => setActiveBar(null)} onFocus={() => setActiveBar({ categoryIndex, seriesIndex })} onMouseEnter={() => setActiveBar({ categoryIndex, seriesIndex })} onMouseLeave={() => setActiveBar(null)} style={{ "--bar-color": seriesItem.color, "--bar-height": height }} type="button"><span className="visually-hidden">{seriesItem.label}: {value.toLocaleString()} {valueLabel}</span></button>;
        })}</div><strong className="bar-group-label">{category.label}</strong></div>)}
      </div>
      <div className="grouped-bar-chart-details">
        <p className="chart-hint">Hover or focus a bar for its exact count.</p>
        {selectedBar && <div className="chart-tooltip"><strong>{selectedBar.category.label} · {selectedBar.series.label}</strong><span>{selectedBar.category.values[activeBar.seriesIndex].toLocaleString()} {valueLabel}</span></div>}
        <ul className="chart-legend">{series.map((seriesItem) => <li key={seriesItem.label}><span className="legend-swatch" style={{ backgroundColor: seriesItem.color }} /><span>{seriesItem.label}</span></li>)}</ul>
      </div>
    </section>
  );
}
