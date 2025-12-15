import React, {useState} from 'react';

function App(){
  const [tasksJSON, setTasksJSON] = useState('');
  const [results, setResults] = useState([]);
  const [strategy, setStrategy] = useState('smart');

  const analyze = async () => {
    try {
      const payload = JSON.parse(tasksJSON);

      const resp = await fetch(
        `http://127.0.0.1:8000/api/tasks/analyze/?strategy=${strategy}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }
      );

      const data = await resp.json();
      setResults(data);

    } catch (e) {
      alert('Invalid JSON or server error: ' + e.message);
    }
  };

  return (
    <div style={{padding:20}}>
      <h2>Smart Task Analyzer</h2>
      <textarea rows={10} cols={60} value={tasksJSON}
        onChange={e=>setTasksJSON(e.target.value)}
        placeholder='Paste JSON array of tasks here'/>
      <br/>
      <select value={strategy} onChange={e=> setStrategy(e.target.value)}>
        <option value="smart">Smart Balance</option>
        <option value="fastest">Fastest Wins</option>
        <option value="impact">High Impact</option>
        <option value="deadline">Deadline Driven</option>
      </select>
      <button onClick={analyze}>Analyze Tasks</button>

      <h3>Results</h3>
      <ul>
        {results.map(r=>(
          <li key={r.id}>
            <strong>{r.title}</strong><br/>
            Score: {r.score}<br/>
            Reason: urgency={r.explanation.urgency},
            importance={r.explanation.importance},
            effort={r.explanation.effort},
            dependency={r.explanation.dependency}
          </li>
        ))}
      </ul>
    </div>
  );
}
export default App;
