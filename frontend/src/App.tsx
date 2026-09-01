import { useEffect, useState } from "react";

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
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [energy, setEnergy] = useState<EnergyRow[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/buildings`).then(r => r.json()).then(setBuildings);
    fetch(`${API_BASE}/rooms`).then(r => r.json()).then(setRooms);
    fetch(`${API_BASE}/energy`).then(r => r.json()).then(setEnergy);
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
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
  );
}

export default App;