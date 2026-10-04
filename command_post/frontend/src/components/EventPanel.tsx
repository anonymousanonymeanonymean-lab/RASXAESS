import type { EventData } from "../types";

const ICON: Record<string, string> = {
  FIRE: "🔥",
  GAS: "☢",
  VICTIM: "👤",
  OBSTACLE: "⬛",
  HAZARD: "⚠",
  UNKNOWN: "?",
};

export default function EventPanel({
  events,
  onSelect,
  selectedId,
}: {
  events: EventData[];
  onSelect: (e: EventData) => void;
  selectedId?: string;
}) {
  return (
    <div>
      <h3>EVENTS ({events.length})</h3>
      {events.map((e) => (
        <div
          key={e.event_id}
          className={`event-item ${selectedId === e.event_id ? "selected" : ""} ${
            e.status.toLowerCase()
          }`}
          onClick={() => onSelect(e)}
        >
          <span style={{ fontSize: 16 }}>{ICON[e.event_type] ?? "?"}</span>
          <span style={{ flex: 1 }}>
            <div>
              <b>{e.event_type}</b> · {e.source_id}
            </div>
            <small style={{ color: "#8b949e" }}>
              {e.age_seconds.toFixed(0)}s · {e.severity} · {(e.confidence * 100).toFixed(0)}%
            </small>
          </span>
          <span className={`badge badge-${e.severity}`}>{e.severity}</span>
        </div>
      ))}
    </div>
  );
}