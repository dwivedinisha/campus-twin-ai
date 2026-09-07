import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";
const ROOMS = ["A101","A102","A103","A104","A105","A106","A107","A108","A109","A110",
               "B101","B102","B103","B104","B105","B106","B107","B108","B109","B110",
               "C101","C102","C103","C104","C105","C106","C107","C108","C109","C110"];

function WhatIf() {
  const [roomId, setRoomId] = useState("A101");
  const [acOn, setAcOn] = useState<boolean | null>(null);
  const [occupancy, setOccupancy] = useState<string>("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = async () => {
    setLoading(true);
    const body: any = { room_id: roomId };
    if (acOn !== null) body.ac_on = acOn;
    if (occupancy !== "") body.occupancy = parseInt(occupancy);

    const res = await fetch(`${API_BASE}/simulation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    setResult(await res.json());
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-6">What-If Simulation</h1>

      <div className="bg-slate-800 p-6 rounded-lg max-w-xl space-y-4">
        <div>
          <label className="block text-sm text-slate-400 mb-1">Room</label>
          <select className="bg-slate-700 rounded px-3 py-2 w-full" value={roomId} onChange={e => setRoomId(e.target.value)}>
            {ROOMS.map(r => <option key={r}>{r}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-sm text-slate-400 mb-1">AC Status</label>
          <select
            className="bg-slate-700 rounded px-3 py-2 w-full"
            value={acOn === null ? "" : acOn ? "on" : "off"}
            onChange={e => setAcOn(e.target.value === "" ? null : e.target.value === "on")}
          >
            <option value="">No change</option>
            <option value="on">Turn ON</option>
            <option value="off">Turn OFF</option>
          </select>
        </div>

        <div>
          <label className="block text-sm text-slate-400 mb-1">Hypothetical Occupancy (optional)</label>
          <input
            type="number" className="bg-slate-700 rounded px-3 py-2 w-full"
            value={occupancy} onChange={e => setOccupancy(e.target.value)} placeholder="Leave blank for no change"
          />
        </div>

        <button onClick={runSimulation} disabled={loading} className="bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded w-full">
          {loading ? "Running..." : "Run Simulation"}
        </button>
      </div>

      {result && (
        <div className="mt-6 grid grid-cols-2 gap-4 max-w-2xl">
          <div className="bg-slate-800 p-4 rounded">
            <h3 className="text-slate-400 text-sm mb-2">Current</h3>
            <p className="text-2xl font-bold">{result.current.power_kw} kW</p>
            <p className="text-sm text-slate-400">AC: {result.current.ac_on ? "ON" : "OFF"} · Occupancy: {result.current.occupancy}</p>
          </div>
          <div className="bg-slate-800 p-4 rounded">
            <h3 className="text-slate-400 text-sm mb-2">Simulated</h3>
            <p className="text-2xl font-bold text-emerald-400">{result.simulated.power_kw} kW</p>
            <p className="text-sm text-slate-400">AC: {result.simulated.ac_on ? "ON" : "OFF"} · Occupancy: {result.simulated.occupancy}</p>
          </div>
          <div className="col-span-2 bg-slate-800 p-4 rounded text-center">
            <p className="text-sm text-slate-400">Estimated Difference</p>
            <p className={`text-3xl font-bold ${result.estimated_difference_kw > 0 ? "text-emerald-400" : "text-red-400"}`}>
              {result.estimated_difference_kw > 0 ? "-" : "+"}{Math.abs(result.estimated_difference_kw)} kW
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default WhatIf;