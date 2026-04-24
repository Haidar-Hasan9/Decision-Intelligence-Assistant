import { useState } from 'react';
import axios from 'axios';
import {
  Container, Row, Col, Form, Button, Card, ListGroup,
  Spinner, Table
} from 'react-bootstrap';
import Header from './components/Header';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (text) => {
    const query = text || input;
    if (!query.trim()) return;
    setLoading(true);
    const newMessages = [...messages, { role: 'user', content: query }];
    setMessages(newMessages);
    setInput('');

    try {
      const [ragRes, nonRagRes, mlRes, llmPrioRes] = await Promise.all([
        axios.post('/api/llm/rag', { query }),
        axios.post('/api/llm/non-rag', { query }),
        axios.post('/api/ml/predict', { text: query }),
        axios.post('/api/llm/priority', { query }),
      ]);
      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          data: {
            rag: ragRes.data,
            nonRag: nonRagRes.data,
            ml: mlRes.data,
            llmPrio: llmPrioRes.data,
          },
        },
      ]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header />

      <Container fluid className="main-container">
        <Row className="h-100">
          {/* Chat area */}
          <Col className="chat-col">
            <div className="chat-messages">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message-bubble ${msg.role}`}>
                  {msg.role === 'user' ? (
                    <p className="mb-0">{msg.content}</p>
                  ) : (
                    <div className="bot-response">
                      <Card className="mb-2">
                        <Card.Body>
                          <h5>RAG Answer</h5>
                          <p>{msg.data.rag.answer}</p>
                          <small className="text-muted">
                            {msg.data.rag.latency_ms} ms · ${msg.data.rag.cost_usd.toFixed(6)}
                          </small>
                          <h6 className="mt-2">Sources</h6>
                          <ListGroup>
                            {msg.data.rag.sources.map((src, i) => (
                              <ListGroup.Item key={i}>
                                <strong>{src.id}</strong>: {src.document} (sim: {src.similarity.toFixed(2)})
                              </ListGroup.Item>
                            ))}
                          </ListGroup>
                        </Card.Body>
                      </Card>

                      <Card className="mb-2">
                        <Card.Body>
                          <h5>Non‑RAG Answer</h5>
                          <p>{msg.data.nonRag.answer}</p>
                          <small className="text-muted">
                            {msg.data.nonRag.latency_ms} ms · ${msg.data.nonRag.cost_usd.toFixed(6)}
                          </small>
                        </Card.Body>
                      </Card>

                      <h5>Priority Prediction Comparison</h5>
                      <Table bordered size="sm">
                        <thead>
                          <tr>
                            <th>Method</th>
                            <th>Priority</th>
                            <th>Confidence</th>
                            <th>Latency</th>
                            <th>Cost</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td>ML Model</td>
                            <td>{msg.data.ml.priority === 1 ? 'Urgent' : 'Normal'}</td>
                            <td>{msg.data.ml.confidence.toFixed(4)}</td>
                            <td>~2 ms</td>
                            <td>$0.00</td>
                          </tr>
                          <tr>
                            <td>LLM Zero‑shot</td>
                            <td>{msg.data.llmPrio.priority === 1 ? 'Urgent' : 'Normal'}</td>
                            <td>{msg.data.llmPrio.confidence.toFixed(4)}</td>
                            <td>{msg.data.llmPrio.latency_ms} ms</td>
                            <td>${msg.data.llmPrio.cost_usd.toFixed(6)}</td>
                          </tr>
                        </tbody>
                      </Table>
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="message-bubble assistant">
                  <Spinner animation="border" size="sm" />
                </div>
              )}
            </div>

            <div className="chat-input p-3">
              <Form
                className="d-flex"
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
              >
                <Form.Control
                  type="text"
                  placeholder="Ask about a ticket..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />
                <Button variant="primary" type="submit" disabled={loading}>
                  Send
                </Button>
              </Form>
            </div>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;