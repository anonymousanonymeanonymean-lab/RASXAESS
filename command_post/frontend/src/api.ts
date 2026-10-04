import type {
  AlertData,
  BeaconData,
  EventData,
  RobotData,
} from "./types";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${API}${path}`);
  if (!r.ok) throw new Error(`${path} failed: ${r.status}`);
  return (await r.json()) as T;
}

export const api = {
  health: () => get<{ status: string; mqtt_connected: boolean }>("/health"),
  events: () => get<EventData[]>("/api/events"),
  robots: () => get<RobotData[]>("/api/robots"),
  beacons: () => get<BeaconData[]>("/api/beacons"),
  alerts: () => get<AlertData[]>("/api/alerts"),
  ackAlert: (id: string) =>
    fetch(`${API}/api/alerts/${id}/ack`, { method: "POST" }).then((r) => r.json()),
  resolveAlert: (id: string) =>
    fetch(`${API}/api/alerts/${id}/resolve`, { method: "POST" }).then((r) => r.json()),
};