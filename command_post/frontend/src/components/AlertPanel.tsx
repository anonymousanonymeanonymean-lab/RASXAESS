import type { AlertData } from "../types";

export default function AlertPanel({
  alerts,
  onAck,
  onResolve,
}: {
  alerts: AlertData[];
  onAck: (id: string) => void;
  onResolve: (id: string) => void;
}) {
  return (
    <div>
      <h3>ALERTS ({alerts.length})</h3>
      {alerts.length === 0 && (
        <div style={{ color: "#8b949e" }}>no active alerts</div>
      )}
      {alerts.map((a) => (
        <div key={a.alert_id} className={`alert-item sev-${a.severity}`}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <b>{a.severity}</b>
            <small style={{ color: "#8b949e" }}>{a.status}</small>
          </div>
          <div style={{ margin: "2px 0" }}>{a.message}</div>
          <div style={{ display: "flex", gap: 6, marginTop: 4 }}>
            {a.status === "OPEN" && (
              <button className="btn" onClick={() => onAck(a.alert_id)}>
                ACK
              </button>
            )}
            {a.status !== "RESOLVED" && (
              <button className="btn" onClick={() => onResolve(a.alert_id)}>
                RESOLVE
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}