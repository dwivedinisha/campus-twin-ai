import { useEffect, useState } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const API_BASE = "http://127.0.0.1:8000";

function EnergyAnalytics() {
  const [hourly, setHourly] = useState([]);
  const [byBuilding, setByBuilding] = useState([]);
  const [roomSeries, setRoomSeries] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState("A101");

  useEffect(() => {
    fetch(`${API_BASE}/energy/hourly`).then(r => r.json()).then(setHourly);
    fetch(`${API_BASE}/energy/by-building`).then(r => r.json()).then(setByBuilding);
  }, []);

  useEffect(() => {
    fetch(`${API_BASE}/energy/by-room/${selectedRoom}?limit=100`).then(r => r.json()).then(setRoomSeries);
  }, [selectedRoom]);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-6">Energy Analytics</h1>

      <h2 className="text-xl font-semibold mb-2">Avg Power by Hour of Day</h2>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={hourly}>
          <CartesianGrid stroke="#334155" />
          <XAxis dataKey="hour" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ background: "#1e293b", border: "none" }} />
          <Line type="monotone" dataKey="avg_power_kw" stroke="#34d399" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>

      <h2 className="text-xl font-semibold mt-8 mb-2">Avg Power by Building</h2>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={byBuilding}>
          <CartesianGrid stroke="#334155" />
          <XAxis dataKey="building_id" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ background: "#1e293b", border: "none" }} />
          <Bar dataKey="avg_power_kw" fill="#60a5fa" />
        </BarChart>
      </ResponsiveContainer>

      <h2 className="text-xl font-semibold mt-8 mb-2">
        Room Power Over Time —
        <select
          className="ml-2 bg-slate-800 rounded px-2 py-1"
          value={selectedRoom}
          onChange={e => setSelectedRoom(e.target.value)}
        >
          {["A101","A102","B101","B102","C101","C102"].map(r => <option key={r}>{r}</option>)}
        </select>
      </h2>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={roomSeries}>
          <CartesianGrid stroke="#334155" />
          <XAxis dataKey="timestamp" stroke="#94a3b8" hide />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ background: "#1e293b", border: "none" }} />
          <Line type="monotone" dataKey="power_kw" stroke="#f472b6" strokeWidth={1.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default EnergyAnalytics;