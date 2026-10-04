import type { RobotData } from "../types";

export default function RobotPanel({ robots }: { robots: RobotData[] }) {
  return (
    <div>
      <h3>ROBOTS</h3>
      {robots.length === 0 && <div style={{ color: "#8b949e" }}>no robots</div>}
      {robots.map((r) => (
        <div key={r.robot_id} className="row">
          <span>
            <span className={`status-dot ${r.communication_status === "ONLINE" ? "dot-ok" : "dot-warn"}`} />
            {r.robot_id} <small>({r.robot_type})</small>
          </span>
          <span style={{ color: "#8b949e" }}>
            {r.battery != null ? `${r.battery}%` : "—"} · {r.status}
          </span>
        </div>
      ))}
    </div>
  );
}