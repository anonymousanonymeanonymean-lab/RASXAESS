import type { BeaconData, EventData, RobotData } from "../types";

/**
 * Local ENU canvas view (no GPS).
 * X = East (right), Y = North (up).
 */
export default function LocalCanvasMap({
  events, robots, beacons, onSelect, selectedId,
}: {
  events: EventData[];
  robots: RobotData[];
  beacons: BeaconData[];
  onSelect: (e: EventData) => void;
  selectedId?: string;
}) {
  const pts: { x: number; y: number; kind: string; label: string; id: string; severity?: string }[] = [];
  robots.forEach((r) => r.local_x != null && r.local_y != null &&
    pts.push({ x: r.local_x, y: r.local_y, kind: "robot", label: r.robot_id, id: r.robot_id }));
  beacons.forEach((b) => b.local_x != null && b.local_y != null &&
    pts.push({ x: b.local_x, y: b.local_y, kind: "beacon", label: b.beacon_id, id: b.beacon_id }));
  events.forEach((e) => e.local_x != null && e.local_y != null &&
    pts.push({ x: e.local_x, y: e.local_y, kind: "event", label: e.event_type, id: e.event_id, severity: e.severity }));

  const W = 800, H = 500, PAD = 40;
  const xs = pts.map((p) => p.x); const ys = pts.map((p) => p.y);
  const minX = Math.min(-5, ...xs), maxX = Math.max(5, ...xs);
  const minY = Math.min(-5, ...ys), maxY = Math.max(5, ...ys);
  const sx = (x: number) => PAD + ((x - minX) / (maxX - minX)) * (W - 2 * PAD);
  const sy = (y: number) => H - PAD - ((y - minY) / (maxY - minY)) * (H - 2 * PAD);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "100%" }}>
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#232a33" strokeWidth="1" />
        </pattern>
      </defs>
      <rect width={W} height={H} fill="#0e1116" />
      <rect width={W} height={H} fill="url(#grid)" />

      {/* Origin / ONA */}
      <g>
        <circle cx={sx(0)} cy={sy(0)} r={10} fill="#58a6ff" opacity="0.9" />
        <text x={sx(0) + 14} y={sy(0) + 4} fill="#8b949e" fontSize="11">ONA</text>
      </g>

      {pts.map((p) => {
        const cx = sx(p.x), cy = sy(p.y);
        const color = p.kind === "robot" ? "#58a6ff"
                    : p.kind === "beacon" ? "#3fb950"
                    : p.severity === "CRITICAL" ? "#ff2d55"
                    : p.severity === "HIGH" ? "#f0883e"
                    : "#d29922";
        const r = p.kind === "event" ? 8 : 6;
        return (
          <g key={p.kind + p.id} style={{ cursor: "pointer" }}
             onClick={() => {
               const ev = events.find((e) => e.event_id === p.id);
               if (ev) onSelect(ev);
             }}>
            <circle cx={cx} cy={cy} r={r + 4} fill={color} opacity={0.15} />
            <circle cx={cx} cy={cy} r={r} fill={color}
                    stroke={selectedId === p.id ? "#fff" : "transparent"} strokeWidth={2} />
            <text x={cx + 10} y={cy + 4} fill="#e6edf3" fontSize="11">{p.label}</text>
          </g>
        );
      })}
    </svg>
  );
}