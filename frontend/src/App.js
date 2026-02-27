import React, { useState } from "react";
import axios from "axios";

function App() {
  const [topic, setTopic] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    const res = await axios.post("http://localhost:8000/generate", {
      topic: topic,
    });
    setResult(res.data);
    setLoading(false);
  };

  return (
    <div style={{ padding: 40 }}>
      <h2>AI YouTube Agent</h2>
      <input
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter topic"
      />
      <button onClick={generate}>Generate & Upload</button>

      {loading && <p>Processing...</p>}
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

export default App;