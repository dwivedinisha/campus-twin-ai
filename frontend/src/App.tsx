import { useEffect, useState } from "react";
import EnergyAnalytics from "./EnergyAnalytics";
import WhatIf from "./WhatIf";
import Recommendations from "./Recommendations";
import Assistant from "./Assistant";


interface Building {
  id: number;
  name: string;
}

interface Room {
  id: number;
  building_id: number;
  name: string;
  capacity: number;
}

interface EnergyRow {
  room_id: string;
  building_id: string;
  avg_power_kw: number;
}

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [page, setPage] = useState<"dashboard" | "analytics" | "whatif" | "recommendations" | "assistant">("dashboard");
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [energy, setEnergy] = useState<EnergyRow[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/buildings`).then(r => r.json()).then(setBuildings);
    fetch(`${API_BASE}/rooms`).then(r => r.json()).then(setRooms);
    fetch(`${API_BASE}/energy`).then(r => r.json()).then(setEnergy);
  }, []);

  if (page === "analytics") {
    return <div><NavBar setPage={setPage} /><EnergyAnalytics /></div>;
  }
  if (page === "whatif") {
    return <div><NavBar setPage={setPage} /><WhatIf /></div>;
  }
  if (page === "recommendations") {
    return <div><NavBar setPage={setPage} /><Recommendations /></div>;
  }
  if (page === "assistant") {
    return <div><NavBar setPage={setPage} /><Assistant /></div>;
  }

    return (
    <div className="min-h-screen bg-slate-900 text-white">
      <NavBar setPage={setPage} />
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-6">CampusTwin AI</h1>

        <h2 className="text-xl font-semibold mb-2">Buildings ({buildings.length})</h2>
        <div className="flex gap-4 mb-8">
          {buildings.map(b => (
            <div key={b.id} className="bg-slate-800 px-4 py-2 rounded">{b.name}</div>
          ))}
        </div>

        <h2 className="text-xl font-semibold mb-2">Rooms ({rooms.length})</h2>
        <div className="grid grid-cols-6 gap-3 mb-8">
          {rooms.map(r => (
            <div key={r.id} className="bg-slate-800 p-3 rounded text-center">
              <div className="font-medium">{r.name}</div>
              <div className="text-sm text-slate-400">cap {r.capacity}</div>
            </div>
          ))}
        </div>

        <h2 className="text-xl font-semibold mb-2">Avg Power per Room (kW)</h2>
        <div className="grid grid-cols-6 gap-3">
          {energy.map(e => (
            <div key={e.room_id} className="bg-slate-800 p-3 rounded text-center">
              <div className="font-medium">{e.room_id}</div>
              <div className="text-sm text-emerald-400">{e.avg_power_kw} kW</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}



function NavBar({ setPage }: { setPage: (p: any) => void }) {
  return (
    <div className="flex gap-2 p-4 bg-slate-800">
      <button onClick={() => setPage("dashboard")} className="px-3 py-1.5 rounded hover:bg-slate-700">Dashboard</button>
      <button onClick={() => setPage("analytics")} className="px-3 py-1.5 rounded hover:bg-slate-700">Analytics</button>
      <button onClick={() => setPage("whatif")} className="px-3 py-1.5 rounded hover:bg-slate-700">What-If</button>
      <button onClick={() => setPage("recommendations")} className="px-3 py-1.5 rounded hover:bg-slate-700">Recommendations</button>
      <button onClick={() => setPage("assistant")} className="px-3 py-1.5 rounded hover:bg-slate-700">Assistant</button>
    </div>
  );
}
export default App;