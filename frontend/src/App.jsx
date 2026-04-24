import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [query, setQuery] = useState("");
  const [ragResult, setRagResult] = useState(null);
  const [nonRagResult, setNonRagResult] = useState(null);
  const [mlResult, setMlResult] = useState(null);
  const [llmPriorityResult, setLlmPriorityResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      // Call all four endpoints in parallel
      const [ragRes, nonRagRes, mlRes, llmPrioRes] = await Promise.all([
        axios.post('/api/llm/rag', { query }),
        axios.post('/api/llm/non-rag', { query }),
        axios.post('/api/ml/predict', { text: query }),
        axios.post('/api/llm/priority', { query }),
      ]);

      setRagResult(ragRes.data);
      setNonRagResult(nonRagRes.data);
      setMlResult(mlRes.data);
      setLlmPriorityResult(llmPrioRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Decision Intelligence Assistant</h1>
      <div className="input-section">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your support query..."
          onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
        />
        <button onClick={handleQuery} disabled={loading}>
          {loading ? 'Loading...' : 'Ask'}
        </button>
      </div>

      {ragResult && (
        <div className="results">
          {/* RAG Answer */}
          <div className="answer-panel">
            <h2>RAG Answer</h2>
            <p>{ragResult.answer}</p>
            <p className="meta">Latency: {ragResult.latency_ms} ms | Cost: ${ragResult.cost_usd}</p>
            <h3>Sources</h3>
            <ul>
              {ragResult.sources.map((src, idx) => (
                <li key={idx}>
                  <strong>{src.id}</strong>: {src.document} (similarity: {src.similarity.toFixed(2)})
                </li>
              ))}
            </ul>
          </div>

          {/* Non‑RAG Answer */}
          <div className="answer-panel">
            <h2>Non‑RAG Answer</h2>
            <p>{nonRagResult.answer}</p>
            <p className="meta">Latency: {nonRagResult.latency_ms} ms | Cost: ${nonRagResult.cost_usd}</p>
          </div>

          {/* Comparison Section */}
          <div className="comparison-section">
            <h2>Priority Prediction Comparison</h2>
            <table>
              <thead>
                <tr>
                  <th>Method</th>
                  <th>Priority</th>
                  <th>Confidence</th>
                  <th>Latency (ms)</th>
                  <th>Cost (USD)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>ML Model</td>
                  <td>{mlResult.priority === 1 ? 'Urgent' : 'Normal'}</td>
                  <td>{mlResult.confidence.toFixed(4)}</td>
                  <td>~2 ms (local)</td>
                  <td>$0.00</td>
                </tr>
                <tr>
                  <td>LLM Zero‑shot</td>
                  <td>{llmPriorityResult.priority === 1 ? 'Urgent' : 'Normal'}</td>
                  <td>{llmPriorityResult.confidence.toFixed(4)}</td>
                  <td>{llmPriorityResult.latency_ms} ms</td>
                  <td>${llmPriorityResult.cost_usd}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;