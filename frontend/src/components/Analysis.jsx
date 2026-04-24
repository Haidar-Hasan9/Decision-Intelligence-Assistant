import { useState } from 'react';
import axios from 'axios';
import { Card, Container, Row, Col, Button, Form } from 'react-bootstrap';

const Analysis = () => {
  const [query, setQuery] = useState('');
  const [rag, setRag] = useState(null);
  const [nonRag, setNonRag] = useState(null);
  const [ml, setMl] = useState(null);
  const [llmPrio, setLlmPrio] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const [ragRes, nonRagRes, mlRes, llmPrioRes] = await Promise.all([
        axios.post('/api/llm/rag', { query }),
        axios.post('/api/llm/non-rag', { query }),
        axios.post('/api/ml/predict', { text: query }),
        axios.post('/api/llm/priority', { query }),
      ]);
      setRag(ragRes.data);
      setNonRag(nonRagRes.data);
      setMl(mlRes.data);
      setLlmPrio(llmPrioRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container fluid className="p-4">
      {/* Input area */}
      <div className="mb-4">
        <h4>New analysis</h4>
        <Form className="d-flex gap-2">
          <Form.Control
            type="text"
            placeholder="Enter your support query..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          />
          <Button variant="primary" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Loading...' : 'Ask'}
          </Button>
        </Form>
      </div>

      {/* Query shown if answered */}
      {rag && (
        <div className="mb-3">
          <p><strong>YOU ASKED</strong><br />"{query}"</p>
        </div>
      )}

      {/* Answers row */}
      {rag && nonRag && (
        <Row className="mb-4">
          <Col md={6}>
            <Card>
              <Card.Body>
                <h5>RAG Answer</h5>
                <p>{rag.answer}</p>
                <small className="text-muted">
                  {rag.latency_ms} ms · ${rag.cost_usd.toFixed(6)}
                </small>
                <hr />
                <h6>Sources</h6>
                <ul>
                  {rag.sources.map((src, i) => (
                    <li key={i}>
                      <small>
                        <strong>{src.id}</strong>: {src.document} (similarity: {src.similarity.toFixed(2)})
                      </small>
                    </li>
                  ))}
                </ul>
              </Card.Body>
            </Card>
          </Col>
          <Col md={6}>
            <Card>
              <Card.Body>
                <h5>Non-RAG Answer</h5>
                <p>{nonRag.answer}</p>
                <small className="text-muted">
                  {nonRag.latency_ms} ms · ${nonRag.cost_usd.toFixed(6)}
                </small>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Priority predictors row */}
      {ml && llmPrio && (
        <Row>
          <Col md={6}>
            <Card>
              <Card.Body>
                <h5>ML Priority Predictor</h5>
                <p>
                  <strong>Priority:</strong> {ml.priority === 1 ? 'Urgent' : 'Normal'} &nbsp;
                  <strong>Confidence:</strong> {ml.confidence.toFixed(4)}
                </p>
                <small className="text-muted">Latency: ~2 ms · Cost: $0.00</small>
                <br />
                <small>Accuracy (on test set): 99.96%</small> {/* from notebook */}
              </Card.Body>
            </Card>
          </Col>
          <Col md={6}>
            <Card>
              <Card.Body>
                <h5>LLM Zero‑shot Priority</h5>
                <p>
                  <strong>Priority:</strong> {llmPrio.priority === 1 ? 'Urgent' : 'Normal'} &nbsp;
                  <strong>Confidence:</strong> {llmPrio.confidence.toFixed(4)}
                </p>
                <small className="text-muted">
                  Latency: {llmPrio.latency_ms} ms · Cost: ${llmPrio.cost_usd.toFixed(6)}
                </small>
                <br />
                <small>Accuracy (on test set): N/A</small> {/* You can later compute and store */}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default Analysis;