import { useState } from "react";

export default function PieChart({ ariaLabel, slices, summaryItems = [], total = null, totalLabel, valueLabel }) {
  const [hoveredSliceIndex, setHoveredSliceIndex] = useState(null);
  const sliceTotal = slices.reduce((totalValue, slice) => totalValue + slice.count, 0);
  const totalValue = total ?? sliceTotal;
  const activeSlice = hoveredSliceIndex === null ? null : slices[hoveredSliceIndex];
  let startAngle = -90;

  if (sliceTotal === 0) {
    return <p className="empty-state">This report has no values.</p>;
  }

  function getPoint(angle) {
    const radians = (angle * Math.PI) / 180;
    return { x: 50 + 40 * Math.cos(radians), y: 50 + 40 * Math.sin(radians) };
  }

  return (
    <div className="pie-chart-layout">
      <div className="pie-chart" role="img" aria-label={ariaLabel}>
        <svg viewBox="0 0 100 100">
          {slices.map((slice, sliceIndex) => {
            const endAngle = startAngle + (slice.count / sliceTotal) * 360;
            const startPoint = getPoint(startAngle);
            const endPoint = getPoint(endAngle);
            const largeArcFlag = endAngle - startAngle > 180 ? 1 : 0;
            const path = `M 50 50 L ${startPoint.x} ${startPoint.y} A 40 40 0 ${largeArcFlag} 1 ${endPoint.x} ${endPoint.y} Z`;
            startAngle = endAngle;
            return <path aria-label={`${slice.label}: ${slice.count.toLocaleString()} ${valueLabel}`} className={sliceIndex === hoveredSliceIndex ? "pie-slice active" : "pie-slice"} d={path} fill={`var(--pie-color-${sliceIndex + 1})`} key={slice.label} onBlur={() => setHoveredSliceIndex(null)} onFocus={() => setHoveredSliceIndex(sliceIndex)} onMouseEnter={() => setHoveredSliceIndex(sliceIndex)} onMouseLeave={() => setHoveredSliceIndex(null)} tabIndex="0" />;
          })}
        </svg>
      </div>
      <div className="pie-chart-details">
        <p className="chart-hint">Hover or focus a slice for its exact count.</p>
        {activeSlice && <div className="chart-tooltip"><strong>{activeSlice.label}</strong><span>{activeSlice.count.toLocaleString()} {valueLabel}</span><span>{((activeSlice.count / sliceTotal) * 100).toFixed(1)}%</span></div>}
        <ul className="chart-legend">
          {slices.map((slice, sliceIndex) => <li key={slice.label}><span className="legend-swatch" style={{ backgroundColor: `var(--pie-color-${sliceIndex + 1})` }} /><span>{slice.label}</span><strong>{((slice.count / sliceTotal) * 100).toFixed(1)}%</strong></li>)}
        </ul>
        <div className="chart-total"><span>{totalLabel}</span><strong>{totalValue.toLocaleString()}</strong></div>
        {summaryItems.map((summaryItem) => <div className="chart-total" key={summaryItem.label}><span>{summaryItem.label}</span><strong>{summaryItem.value.toLocaleString()}</strong></div>)}
      </div>
    </div>
  );
}
