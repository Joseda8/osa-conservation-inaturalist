export default function InfoTooltip({ children, label }) {
  return (
    <span className="info-tooltip">
      <button aria-label={label} className="info-tooltip-button" type="button">i</button>
      <span className="info-tooltip-content" role="tooltip">{children}</span>
    </span>
  );
}
