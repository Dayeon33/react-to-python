import { useState } from "react";

type AskResponse = {
  question: string;
  answer: string;
};

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // validation
    if (!question.trim()) {
      setErrorMsg("Please enter a question.");
      return;
    }

    setLoading(true);
    setErrorMsg("");
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8090/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
      }

      const data: AskResponse = await res.json();
      setResult(data);
      setQuestion("");
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to communicate with server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{ maxWidth: 720, margin: "40px auto", fontFamily: "sans-serif" }}
    >
      <h2>React → FastAPI → GPT</h2>

      {/* form with one input and submit button */}
      <form onSubmit={onSubmit} style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your question"
          style={{ flex: 1, padding: 8 }}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Sending..." : "Submit"}
        </button>
      </form>

      {/* error handling */}
      {errorMsg && <p style={{ color: "red" }}>{errorMsg}</p>}

      {/* output */}
      {result && (
        <div style={{ marginTop: 20 }}>
          <p>
            <strong>Question:</strong>
            <br />
            {result.question}
          </p>
          <p>
            <strong>Answer:</strong>
            <br />
            {result.answer}
          </p>
        </div>
      )}
    </div>
  );
}

export default App;
