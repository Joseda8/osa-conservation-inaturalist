export default function SeriesSelector({ items, onToggle, selectedItemIds }) {
  if (items.length < 2) {
    return null;
  }

  return <div aria-label="Choose chart entries to show" className="series-selector"><span>Show:</span>{items.map((item) => {
    const isSelected = selectedItemIds.includes(item.id);
    return <button aria-pressed={isSelected} className={isSelected ? "series-selector-item active" : "series-selector-item"} disabled={isSelected && selectedItemIds.length === 1} key={item.id} onClick={() => onToggle(item.id)} type="button"><span className="legend-swatch" style={{ backgroundColor: item.color }} />{item.label}</button>;
  })}</div>;
}
