import { useEffect, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";

const API = "http://127.0.0.1:8000";

export default function Campus3D() {
  const [twin, setTwin] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [sel, setSel] = useState<string | null>(null);
  const [building, setBuilding] = useState("ALL");

  const refresh = () => {
    fetch(`${API}/twin`).then(r => r.json()).then(setTwin);
    fetch(`${API}/alerts`).then(r => r.json()).then(setAlerts);
  };

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 3000);
    return () => clearInterval(id);
  }, []);

    const control = async (room: string, body: any) => {
    setTwin(prev => prev.map(r => r.room_id === room ? { ...r, ac_status: body.ac_on ? "ON" : "OFF" } : r));
    await fetch(`${API}/twin/${room}/control`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    refresh();
  };

  const clearOverride = async (room: string) => {
    await fetch(`${API}/twin/${room}/clear-override`, { method: "POST" });
    refresh();
  };

  const room = twin.find(r => r.room_id === sel);
  const alert = alerts.find(a => a.room_id === sel);
  const buildings = [...new Set(twin.map(r => r.building_id))].sort();
  const shown = building === "ALL" ? twin : twin.filter(r => r.building_id === building);
  const grouped: Record<string, any[]> = {};
  shown.forEach(r => (grouped[r.building_id] ??= []).push(r));
  const names = Object.keys(grouped).sort();
  const perRow = building === "ALL" ? 5 : 1;

  return (
    <div className="min-h-screen bg-slate-900 text-white flex">
      <div className="flex-1 relative">
        <select
          className="absolute top-4 left-4 z-10 bg-slate-800 rounded px-2 py-1 text-sm"
          value={building}
          onChange={e => { setBuilding(e.target.value); setSel(null); }}
        >
          <option value="ALL">All Buildings</option>
          {buildings.map(b => <option key={b}>{b}</option>)}
        </select>

        <Canvas camera={{ position: [0, 15, 30], fov: 55 }}>
          <ambientLight intensity={0.6} />
          <directionalLight position={[10, 15, 5]} intensity={0.8} />
          <OrbitControls />
          {names.map((b, bi) => {
            const rooms = grouped[b].sort((a, c) => a.room_id.localeCompare(c.room_id));
            const cols = Math.min(5, rooms.length);
            const rows = Math.ceil(rooms.length / 5);
            const x = (bi % perRow) * 10 - ((perRow - 1) * 10) / 2;
            const z = Math.floor(bi / perRow) * 14;
            return (
              <group key={b}>
                <mesh position={[x, -0.5, z]}>
                  <boxGeometry args={[cols * 1.1, 0.2, rows * 1.5]} />
                  <meshStandardMaterial color="#1e293b" />
                </mesh>
                <Text position={[x, -0.9, z + rows * 0.8]} fontSize={0.3} color="#94a3b8">{b}</Text>
                {rooms.map((r, i) => {
                  const color = sel === r.room_id ? "#3b82f6" : r.status === "ALERT" ? "#ef4444" : r.ac_status === "ON" ? "#10b981" : "#475569";
                  return (
                    <group
                      key={r.room_id}
                      position={[x - cols / 2 + (i % 5), 0.1, z - rows / 2 + Math.floor(i / 5) * 1.3]}
                      onClick={(e) => { e.stopPropagation(); setSel(r.room_id); }}
                    >
                      <mesh>
                        <boxGeometry args={[0.9, 0.8, 0.9]} />
                        <meshStandardMaterial color={color} />
                      </mesh>
                      <Text position={[0, 0.6, 0]} fontSize={0.18} color="white">{r.room_id}</Text>
                    </group>
                  );
                })}
              </group>
            );
          })}
        </Canvas>
      </div>

      <div className="w-80 bg-slate-800 p-6 overflow-y-auto text-sm">
        <h2 className="text-xl font-bold mb-4">Room Details</h2>
        {room ? (
          <div className="space-y-2">
            <p>Room: {room.room_id}</p>
            <p>Building: {room.building_id}</p>
            <p>Occupancy: {room.occupancy}/{room.capacity}</p>
            <p>Temp: {room.temperature_c}°C</p>
            <p>AC: {room.ac_status}</p>
            <p>Power: {room.power_kw} kW</p>
            <p className={room.status === "ALERT" ? "text-red-400" : "text-emerald-400"}>Status: {room.status}</p>

            {room.status === "ALERT" && (
              <div className="bg-red-950 border border-red-800 rounded p-3 text-red-300 text-xs space-y-1">
                <p className="font-semibold">⚠ Anomaly Detected</p>
                <p>Type: {room.anomaly_type ?? "Unknown"}</p>
              </div>
            )}

            <div className="pt-4 border-t border-slate-700 space-y-2">
              <p className="text-slate-400 text-xs uppercase">Manual Control</p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => control(room.room_id, { ac_on: true })}
                  className="flex-1 bg-emerald-700 rounded py-1.5 cursor-pointer"
                >
                  AC ON
                </button>
                <button
                  type="button"
                  onClick={() => control(room.room_id, { ac_on: false })}
                  className="flex-1 bg-slate-600 rounded py-1.5 cursor-pointer"
                >
                  AC OFF
                </button>
              </div>
              <button
                type="button"
                onClick={() => clearOverride(room.room_id)}
                className="w-full bg-slate-700 rounded py-1.5 text-xs cursor-pointer"
              >
                Clear Override
              </button>
            </div>
          </div>
        ) : (
          <p className="text-slate-500">Click a room. ({shown.length} shown)</p>
        )}

        {alerts.length > 0 && (
          <div className="mt-6 pt-4 border-t border-slate-700">
            <p className="text-slate-400 text-xs uppercase mb-2">Active Alerts ({alerts.length})</p>
            {alerts.map(a => (
              <button
                type="button"
                key={a.room_id}
                onClick={() => setSel(a.room_id)}
                className="w-full text-left bg-red-950/50 px-2 py-1.5 rounded text-xs text-red-300 mb-1 cursor-pointer"
              >
                {a.room_id} — {a.power_residual > 0 ? "+" : ""}{a.power_residual} kW
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}