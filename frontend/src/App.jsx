import { useState } from 'react';
import Sidebar from './components/Sidebar';
import RecentQueries from './components/RecentQueries';
import Analysis from './components/Analysis';
import { Row, Col } from 'react-bootstrap';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const handleSelect = (eventKey) => {
    setActiveTab(eventKey);
  };

  return (
    <div className="d-flex">
      <Sidebar activeItem={activeTab} onSelect={handleSelect} />
      <div className="d-flex flex-grow-1">
        <Row className="flex-grow-1">
          <Col md={3} className="bg-light p-3 border-end">
            <RecentQueries />
          </Col>
          <Col md={9} className="p-0">
            <Analysis />
          </Col>
        </Row>
      </div>
    </div>
  );
}

export default App;