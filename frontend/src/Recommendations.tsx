import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

interface Rec {
  id: number;
  room_id: string;
  type: string;
  reason: string;
  proposed_action: string;
  estimated_impact_kw: number | null;
  confidence: number;
  status: string;
  agent_source: string;
}

function Recommendations() {
  const [recs, setRecs] = useState<Rec[]>([]);
  const [generating, setGenerating] = useState(false);

  const load = () => {
    fetch(`${API_BASE}/recommendations?status=PENDING`).then(r => r.json()).then(setRecs);
  };

  useEffect(() => { load(); }, []);

  const generate = async () => {
    setGenerating(true);
    await fetch(`${API_BASE}/recommendations/generate`, { method: "POST" });
    load();
    setGenerating(false);
  };

  const act = async (id: number, action: "approve" | "reject") => {
    await fetch(`${API_BASE}/recommendations/${id}/${action}`, { method: "POST" });
    load();
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Recommendations</h1>
        <button onClick={generate} disabled={generating} className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded">
          {generating ? "Generating..." : "Generate New"}
        </button>
      </div>

      {recs.length === 0 && <p className="text-slate-400">No pending recommendations right now.</p>}

      <div className="space-y-3">
        {recs.map(rec => (
          <div key={rec.id} className="bg-slate-800 p-4 rounded-lg flex justify-between items-center">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs px-2 py-0.5 rounded ${rec.type === "MAINTENANCE" ? "bg-red-900 text-red-300" : "bg-emerald-900 text-emerald-300"}`}>
                  {rec.type}
                </span>
                <span className="text-xs text-slate-500">{rec.agent_source}</span>
              </div>
              <p className="font-medium">{rec.room_id} — {rec.proposed_action}</p>
              <p className="text-sm text-slate-400">{rec.reason}</p>
              {rec.estimated_impact_kw && (
                <p className="text-sm text-emerald-400 mt-1">Est. savings: {rec.estimated_impact_kw} kW</p>
              )}
            </div>
            <div className="flex gap-2">
              <button onClick={() => act(rec.id, "approve")} className="bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 rounded text-sm">Approve</button>
              <button onClick={() => act(rec.id, "reject")} className="bg-slate-600 hover:bg-slate-500 px-3 py-1.5 rounded text-sm">Reject</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Recommendations;