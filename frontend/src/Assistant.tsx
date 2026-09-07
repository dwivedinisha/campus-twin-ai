import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

interface Message {
  role: "user" | "assistant";
  content: string;
}

function Assistant() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    const question = input;
    setMessages(prev => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    const res = await fetch(`${API_BASE}/assistant/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    setMessages(prev => [...prev, { role: "assistant", content: data.answer }]);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8 flex flex-col">
      <h1 className="text-3xl font-bold mb-6">Campus Assistant</h1>

      <div className="flex-1 bg-slate-800 rounded-lg p-4 mb-4 overflow-y-auto max-h-[60vh] space-y-3">
        {messages.length === 0 && (
          <p className="text-slate-500 text-sm">Try asking: "Which rooms are wasting the most energy?" or "Are any rooms showing signs of a malfunction?"</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`p-3 rounded-lg max-w-2xl whitespace-pre-wrap ${m.role === "user" ? "bg-blue-900 ml-auto" : "bg-slate-700"}`}>
            {m.content}
          </div>
        ))}
        {loading && <div className="bg-slate-700 p-3 rounded-lg max-w-2xl text-slate-400">Thinking...</div>}
      </div>

      <div className="flex gap-2">
        <input
          className="flex-1 bg-slate-800 rounded px-4 py-2"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && send()}
          placeholder="Ask about campus energy, occupancy, or alerts..."
        />
        <button onClick={send} className="bg-emerald-600 hover:bg-emerald-500 px-6 py-2 rounded">Send</button>
      </div>
    </div>
  );
}

export default Assistant;