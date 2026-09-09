import { useEffect, useState } from "react";
import { LayoutGrid, Box, Activity, SlidersHorizontal, Sparkles, Bot } from "lucide-react";
import EnergyAnalytics from "./EnergyAnalytics";
import WhatIf from "./WhatIf";
import Recommendations from "./Recommendations";
import Assistant from "./Assistant";
import Campus3D from "./Campus3D";

interface Building { id: number; name: string; }
interface Room { id: number; building_id: number; name: string; capacity: number; }
interface EnergyRow { room_id: string; building_id: string; avg_power_kw: number; }
const API = "http://127.0.0.1:8000";

const NAV = [
  { id: "dashboard", label: "Command Center", icon: LayoutGrid, color: "#22D3EE" },
  { id: "campus3d", label: "3D Digital Twin", icon: Box, color: "#A78BFA", tag: "LIVE", tagColor: "#34D399" },
  { id: "analytics", label: "Energy Analytics", icon: Activity, color: "#34D399" },
  { id: "whatif", label: "Scenario Simulator", icon: SlidersHorizontal, color: "#FBBF24", tag: "SIM", tagColor: "#FBBF24" },
  { id: "recommendations", label: "AI Recommendations", icon: Sparkles, color: "#FB7185" },
  { id: "assistant", label: "Campus Copilot", icon: Bot, color: "#38BDF8", tag: "AI", tagColor: "#38BDF8" },
];

function Sidebar({ page, setPage }: { page: string; setPage: (p: any) => void }) {
  return (
    <div className="w-64 glass min-h-screen flex flex-col p-4">
      <div className="flex items-center gap-3 mb-8 px-2">
        <div className="w-9 h-9 rounded-lg brand-grad" />
        <div>
          <p className="text-white font-semibold text-sm">CampusTwin <span className="text-cyan-400">v2.4</span></p>
          <p className="text-slate-500 text-[10px] mono tracking-wide">OPERATIONS OS</p>
        </div>
      </div>
      <p className="text-slate-500 text-[10px] mono tracking-wide px-2 mb-2">PLATFORM MODULES</p>
      <nav className="space-y-1">
        {NAV.map(item => {
          const Icon = item.icon;
          const active = page === item.id;
          return (
            <button key={item.id} onClick={() => setPage(item.id)}
              style={active ? { borderLeft: `2px solid ${item.color}` } : { borderLeft: "2px solid transparent" }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-r-lg text-sm transition-colors ${
                active ? "bg-white/5 text-white" : "text-slate-400 hover:text-white hover:bg-white/5"}`}>
              <Icon size={16} color={active ? item.color : "#64748B"} />
              <span className="flex-1 text-left">{item.label}</span>
              {item.tag && (
                <span className="text-[9px] mono px-1.5 py-0.5 rounded" style={{ background: `${item.tagColor}22`, color: item.tagColor }}>
                  {item.tag}
                </span>
              )}
            </button>
          );
        })}
      </nav>
      <div className="mt-auto glass rounded-lg p-3 text-[10px] mono text-slate-400 space-y-1">
        <p className="flex justify-between">Physics Engine <span className="text-emerald-400">3s Sync</span></p>
        <p className="flex justify-between">ML Sentinel <span className="text-cyan-400">Active</span></p>
      </div>
    </div>
  );
}

function Header({ title, subtitle, setPage }: { title: string; subtitle: string; setPage: (p: any) => void }) {
  const [time, setTime] = useState(new Date());
  useEffect(() => { const id = setInterval(() => setTime(new Date()), 1000); return () => clearInterval(id); }, []);
  return (
    <div className="glass px-8 py-4 flex items-center justify-between">
      <div>
        <h1 className="text-white text-xl font-semibold">{title}</h1>
        <p className="text-slate-500 text-xs">{subtitle}</p>
      </div>
      <div className="flex items-center gap-3 text-xs">
        <span className="glass px-3 py-1.5 rounded mono text-slate-400">SYS: {time.toLocaleTimeString()}</span>
        <button onClick={() => setPage("assistant")} className="brand-grad px-4 py-1.5 rounded text-white font-medium flex items-center gap-1.5">
          <Bot size={14} /> Ask Copilot
        </button>
      </div>
    </div>
  );
}

function KPI({ label, value, unit, color = "#FFFFFF" }: { label: string; value: string; unit?: string; color?: string }) {
  return (
    <div className="glass rounded-xl p-4">
      <p className="text-slate-500 text-[10px] mono tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-semibold mono" style={{ color }}>{value} <span className="text-sm text-slate-500">{unit}</span></p>
    </div>
  );
}

function Dashboard({ buildings, rooms, energy }: { buildings: Building[]; rooms: Room[]; energy: EnergyRow[] }) {
  const [filter, setFilter] = useState("");
  const [alerts, setAlerts] = useState<any[]>([]);
  const [recs, setRecs] = useState<any[]>([]);
  const [byBuilding, setByBuilding] = useState<any[]>([]);

  useEffect(() => {
    fetch(`${API}/alerts`).then(r => r.json()).then(setAlerts);
    fetch(`${API}/recommendations?status=PENDING`).then(r => r.json()).then(setRecs);
    fetch(`${API}/energy/by-building`).then(r => r.json()).then(setByBuilding);
  }, []);

  const bMap = Object.fromEntries(buildings.map(b => [b.id, b.name]));
  const visibleRooms = filter ? rooms.filter(r => bMap[r.building_id] === filter) : [];
  const visibleNames = new Set(visibleRooms.map(r => r.name));
  const visibleEnergy = energy.filter(e => visibleNames.has(e.room_id));

  const totalCap = rooms.reduce((s, r) => s + r.capacity, 0);
  const avgPower = energy.length ? energy.reduce((s, e) => s + e.avg_power_kw, 0) / energy.length : 0;
  const totalCampusPower = energy.reduce((s, e) => s + e.avg_power_kw, 0);
  const peakBuilding = byBuilding.length ? byBuilding.reduce((a, b) => (a.avg_power_kw > b.avg_power_kw ? a : b)) : null;
  const savingsPotential = recs.reduce((s, r) => s + (r.estimated_impact_kw ?? 0), 0);

  return (
    <div className="p-8">
      <div className="grid grid-cols-4 gap-4 mb-4">
        <KPI label="BUILDINGS" value={String(buildings.length)} color="#22D3EE" />
        <KPI label="TOTAL ROOMS" value={String(rooms.length)} color="#A78BFA" />
        <KPI label="TOTAL CAPACITY" value={String(totalCap)} unit="seats" color="#FBBF24" />
        <KPI label="AVG POWER / ROOM" value={avgPower.toFixed(2)} unit="kW" color="#34D399" />
      </div>
      <div className="grid grid-cols-4 gap-4 mb-8">
        <KPI label="TOTAL CAMPUS LOAD" value={totalCampusPower.toFixed(1)} unit="kW" color="#38BDF8" />
        <KPI label="PEAK BUILDING" value={peakBuilding?.building_id ?? "-"} unit={peakBuilding ? `${peakBuilding.avg_power_kw} kW` : ""} color="#FB923C" />
        <KPI label="ACTIVE ANOMALIES" value={String(alerts.length)} color={alerts.length > 0 ? "#FB7185" : "#34D399"} />
        <KPI label="AI SAVINGS POTENTIAL" value={savingsPotential.toFixed(1)} unit="kW" color="#FB7185" />
      </div>

      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-white font-medium flex items-center gap-2"><LayoutGrid size={16} className="text-cyan-400" /> Building Room Detail</p>
          <select value={filter} onChange={e => setFilter(e.target.value)} className="glass rounded px-3 py-1.5 text-sm text-white bg-transparent">
            <option value="">Select building...</option>
            {buildings.map(b => <option key={b.id} value={b.name} className="bg-slate-900">{b.name}</option>)}
          </select>
        </div>

        {filter ? (
          <div className="grid grid-cols-5 gap-3">
            {visibleRooms.map(r => {
              const e = visibleEnergy.find(e => e.room_id === r.name);
              return (
                <div key={r.id} className="glass rounded-lg p-3 text-center">
                  <p className="text-white text-sm">{r.name}</p>
                  <p className="text-slate-500 text-[10px] mono">cap {r.capacity}</p>
                  <p className="text-emerald-400 text-xs mono mt-1">{e?.avg_power_kw ?? "-"} kW</p>
                </div>
              );
            })}
          </div>
        ) : <p className="text-slate-500 text-sm text-center py-8">Select a building to view room-level telemetry.</p>}
      </div>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [energy, setEnergy] = useState<EnergyRow[]>([]);

  useEffect(() => {
    fetch(`${API}/buildings`).then(r => r.json()).then(setBuildings);
    fetch(`${API}/rooms`).then(r => r.json()).then(setRooms);
    fetch(`${API}/energy`).then(r => r.json()).then(setEnergy);
  }, []);

  const titles: Record<string, [string, string]> = {
    dashboard: ["Command Center", "Live campus-wide operational summary"],
    campus3d: ["3D Digital Twin", "Interactive spatial view of campus state"],
    analytics: ["Energy Analytics", "Diurnal power profiles and benchmarking"],
    whatif: ["Scenario Simulator", "Hypothetical resource optimization"],
    recommendations: ["AI Recommendations", "Agent-generated optimization actions"],
    assistant: ["Campus Copilot", "Ask questions about live campus state"],
  };

  const pages: Record<string, JSX.Element> = {
    dashboard: <Dashboard buildings={buildings} rooms={rooms} energy={energy} />,
    campus3d: <Campus3D />,
    analytics: <EnergyAnalytics />,
    whatif: <WhatIf />,
    recommendations: <Recommendations />,
    assistant: <Assistant />,
  };

  return (
    <div className="flex min-h-screen bg-[#0B0F1A]">
      <Sidebar page={page} setPage={setPage} />
      <div className="flex-1">
        <Header title={titles[page][0]} subtitle={titles[page][1]} setPage={setPage} />
        {pages[page]}
      </div>
    </div>
  );
}