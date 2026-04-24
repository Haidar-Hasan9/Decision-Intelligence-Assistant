import { Card } from 'react-bootstrap';

const recent = [
  { query: 'Refund still not processed after 10 days', time: '2d ago', priority: 'ML urgent' },
  { query: 'My order shows delivered but I never got this...', time: '10m ago', priority: 'ML normal' },
  { query: 'Agent promised a callback but never called', time: '1h ago', priority: 'ML normal' },
];

const RecentQueries = () => {
  return (
    <div className="p-3">
      <h5>RECENT</h5>
      {recent.map((item, idx) => (
        <Card key={idx} className="mb-2">
          <Card.Body>
            <small>{item.query}</small><br />
            <small className="text-muted">{item.time} - {item.priority}</small>
          </Card.Body>
        </Card>
      ))}
    </div>
  );
};

export default RecentQueries;