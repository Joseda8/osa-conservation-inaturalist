export default function DashboardSidebar({ activeSectionId, sections, setActiveSectionId }) {
  return (
    <aside className="sidebar">
      <img alt="OSA Conservation: conserving Costa Rica's natural treasure" className="organization-logo" src={`${import.meta.env.BASE_URL}assets/osa-conservation-logo.png`} />
      <h1>iNaturalist dashboard</h1>
      <nav aria-label="Dashboard sections">
        {sections.map((section) => <button aria-current={section.id === activeSectionId ? "page" : undefined} className={section.id === activeSectionId ? "navigation-item active" : "navigation-item"} key={section.id} onClick={() => setActiveSectionId(section.id)} type="button">{section.label}</button>)}
      </nav>
    </aside>
  );
}
