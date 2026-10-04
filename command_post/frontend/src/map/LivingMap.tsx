import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
import type { BeaconData, EventData, RobotData } from "../types";
import { makeIcon } from "./icons";
import LocalCanvasMap from "./LocalCanvasMap";

const ICON: Record<string, string> = {
  FIRE: "🔥", GAS: "☢", VICTIM: "👤", OBSTACLE: "⬛", HAZARD: "⚠", UNKNOWN: "?",
};

export default function LivingMap({
  events, robots, beacons, onSelect, selectedId,
}: {
  events: EventData[];
  robots: RobotData[];
  beacons: BeaconData[];
  onSelect: (e: EventData) => void;
  selectedId?: string;
}) {
  // Auto-detect: if no item has GPS, use the local ENU canvas.
  const hasGps =
    events.some((e) => e.latitude != null) ||
    robots.some((r) => r.latitude != null) ||
    beacons.some((b) => (b as any).latitude != null);

  if (!hasGps) {
    return (
      <LocalCanvasMap
        events={events}
        robots={robots}
        beacons={beacons}
        onSelect={onSelect}
        selectedId={selectedId}
      />
    );
  }

  // GPS mode
  const allLat = [
    ...events.map((e) => e.latitude).filter((x): x is number => x != null),
    ...robots.map((r) => r.latitude).filter((x): x is number => x != null),
  ];
  const allLon = [
    ...events.map((e) => e.longitude).filter((x): x is number => x != null),
    ...robots.map((r) => r.longitude).filter((x): x is number => x != null),
  ];
  const center: [number, number] = allLat.length
    ? [allLat.reduce((a, b) => a + b, 0) / allLat.length, allLon.reduce((a, b) => a + b, 0) / allLon.length]
    : [36.8065, 10.1815];

  const links = beacons
    .filter((b) => b.parent_id)
    .map((b) => {
      const parent = beacons.find((x) => x.beacon_id === b.parent_id);
      if (!parent) return null;
      const p1: [number, number] = [(b as any).latitude, (b as any).longitude];
      const p2: [number, number] = [(parent as any).latitude, (parent as any).longitude];
      if (p1.some((v) => v == null) || p2.some((v) => v == null)) return null;
      return { id: b.beacon_id, path: [p1, p2] as [number, number][] };
    })
    .filter((x): x is { id: string; path: [number, number][] } => x !== null);

  return (
    <div className="map-container">
      <MapContainer center={center} zoom={16} className="map-wrap">
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {links.map((l) => (
          <Polyline key={l.id} positions={l.path} color="#3fb950" weight={2} opacity={0.6} />
        ))}
        {robots
          .filter((r) => r.latitude != null && r.longitude != null)
          .map((r) => (
            <Marker
              key={r.robot_id}
              position={[r.latitude as number, r.longitude as number]}
              icon={makeIcon(r.robot_type === "WRITER" ? "🤖" : "🚁", "#58a6ff")}
            >
              <Popup>
                <b>{r.robot_id}</b>
                <br />
                {r.status} · {r.battery ?? "—"}%
              </Popup>
            </Marker>
          ))}
        {events
          .filter((e) => e.latitude != null && e.longitude != null)
          .map((e) => (
            <Marker
              key={e.event_id}
              position={[e.latitude as number, e.longitude as number]}
              icon={makeIcon(
                ICON[e.event_type] ?? "?",
                e.severity === "CRITICAL" ? "#ff2d55" : e.severity === "HIGH" ? "#f0883e" : "#d29922",
              )}
              eventHandlers={{ click: () => onSelect(e) }}
            >
              <Popup>
                <b>{e.event_type}</b> · {e.source_id}
                <br />
                {e.age_seconds.toFixed(0)}s · {(e.confidence * 100).toFixed(0)}%
              </Popup>
            </Marker>
          ))}
      </MapContainer>
    </div>
  );
}