import { useState } from "react";

export default function RankedBarChart({ ariaLabel, groups, valueLabel }) {
  const [activeGroupId, setActiveGroupId] = useState(groups[0]?.id ?? null);
  const [activeItemId, setActiveItemId] = useState(null);
  const activeGroup = groups.find((group) => group.id === activeGroupId) ?? groups[0];
  const maximumValue = Math.max(...(activeGroup?.items.map((item) => item.value) ?? []), 0);
  const activeItem = activeGroup?.items.find((item) => item.id === activeItemId) ?? null;

  if (!activeGroup || maximumValue === 0) {
    return <p className="empty-state">This report has no values.</p>;
  }

  function selectGroup(groupId) {
    setActiveGroupId(groupId);
    setActiveItemId(null);
  }

  return (
    <section aria-label={ariaLabel} className="ranked-bar-chart">
      <div aria-label="Choose region" className="ranked-bar-chart-selector">
        <span>Show:</span>
        {groups.map((group) => (
          <button aria-pressed={group.id === activeGroup.id} className={group.id === activeGroup.id ? "ranked-bar-chart-selector-item active" : "ranked-bar-chart-selector-item"} key={group.id} onClick={() => selectGroup(group.id)} style={{ "--ranked-bar-color": group.color }} type="button">
            <span className="legend-swatch" style={{ backgroundColor: group.color }} />
            {group.label}
          </button>
        ))}
      </div>
      <div className="ranked-bar-chart-content">
        <ol className="ranked-bar-chart-list">
          {activeGroup.items.map((item) => (
            <li className="ranked-bar-chart-item" key={item.id}>
              <span aria-hidden="true" className="ranked-bar-rank">{item.rank}</span>
              <div className="ranked-bar-item-content">
                <div className="ranked-bar-item-label">
                  <strong>{item.label}</strong>
                  {item.detail && item.detail !== item.label && <em>{item.detail}</em>}
                </div>
                <button aria-label={`${item.rank}. ${item.label}: ${item.value.toLocaleString()} ${valueLabel}`} className={activeItem?.id === item.id ? "ranked-bar-row active" : "ranked-bar-row"} onBlur={() => setActiveItemId(null)} onFocus={() => setActiveItemId(item.id)} onMouseEnter={() => setActiveItemId(item.id)} onMouseLeave={() => setActiveItemId(null)} style={{ "--ranked-bar-color": activeGroup.color, "--ranked-bar-width": `${(item.value / maximumValue) * 100}%` }} type="button">
                  <span className="ranked-bar-fill" />
                  <strong>{item.value.toLocaleString()}</strong>
                </button>
              </div>
            </li>
          ))}
        </ol>
        <div className="ranked-bar-chart-details">
          <p className="chart-hint">Hover or focus a bar for its exact count.</p>
          <div className={activeItem ? "chart-tooltip active" : "chart-tooltip"}>
            {activeItem ? <><strong>{activeItem.rank}. {activeItem.label}</strong><span>{activeItem.value.toLocaleString()} {valueLabel}</span></> : <span>Select a species bar to see its count.</span>}
          </div>
        </div>
      </div>
    </section>
  );
}
