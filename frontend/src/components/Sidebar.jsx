import { Nav } from 'react-bootstrap';

const Sidebar = ({ activeItem, onSelect }) => {
  const items = [
    { eventKey: 'dashboard', label: 'Dashboard' },
    { eventKey: 'comparison', label: 'Model comparison' },
    { eventKey: 'data-rag', label: 'Data & RAG' },
    { eventKey: 'history', label: 'History' },
    { eventKey: 'health', label: 'System health' },
  ];

  return (
    <div className="d-flex flex-column flex-shrink-0 p-3 bg-light" style={{ width: '280px', minHeight: '100vh' }}>
      <a href="/" className="d-flex align-items-center mb-3 mb-md-0 me-md-auto link-dark text-decoration-none">
        <span className="fs-4">Zap</span>
      </a>
      <hr />
      <Nav className="flex-column mb-auto" activeKey={activeItem} onSelect={onSelect}>
        {items.map((item) => (
          <Nav.Link key={item.eventKey} eventKey={item.eventKey}>
            {item.label}
          </Nav.Link>
        ))}
      </Nav>
    </div>
  );
};

export default Sidebar;