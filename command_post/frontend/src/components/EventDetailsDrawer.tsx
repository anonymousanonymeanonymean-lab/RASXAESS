import type { EventData } from "../types";

export default function EventDetailsDrawer({ event }: { event: EventData | null }) {
  if (!event) {
    return <div style={{ color: "#8b949e" }}>Select an event to inspect details.</div>;
  }
  const pos =
    event.coordinate_reference === "WGS84" && event.latitude != null
      ? `${event.latitude.toFixed(6)}, ${event.longitude?.toFixed(6)}`
      : `local ENU (${event.local_x?.toFixed(2)}, ${event.local_y?.toFixed(2)}, ${event.local_z?.toFixed(2)})`;

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
      <div>
        <h3>EVENT</h3>
        <div className="row"><span>ID</span><span>{event.event_id.slice(0, 8)}…</span></div>
        <div className="row"><span>Type</span><span><b>{event.event_type}</b></span></div>
        <div className="row"><span>Source</span><span>{event.source_id}</span></div>
        <div className="row"><span>Confidence</span><span>{(event.confidence * 100).toFixed(0)}%</span></div>
        <div className="row"><span>Severity</span>
          <span className={`badge badge-${event.severity}`}>{event.severity}</span>
        </div>
      </div>
      <div>
        <h3>TIME</h3>
        <div className="row"><span>Timestamp</span><span>{new Date(event.event_timestamp).toLocaleString()}</span></div>
        <div className="row"><span>Age</span><span>{event.age_seconds.toFixed(0)} s</span></div>
        <div className="row"><span>Status</span><span>{event.status}</span></div>
      </div>
      <div>
        <h3>SPATIAL</h3>
        <div className="row"><span>Frame</span><span>{event.frame_id ?? "—"}</span></div>
        <div className="row"><span>Reference</span><span>{event.coordinate_reference}</span></div>
        <div className="row"><span>Position</span><span>{pos}</span></div>
      </div>
    </div>
  );
}