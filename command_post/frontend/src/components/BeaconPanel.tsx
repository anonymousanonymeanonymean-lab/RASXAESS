import type { BeaconData } from "../types";

export default function BeaconPanel({ beacons }: { beacons: BeaconData[] }) {
  return (
    <div>
      <h3>BEACONS ({beacons.length})</h3>
      {beacons.map((b) => (
        <div key={b.beacon_id} className="row">
          <span>
            <span className="status-dot dot-ok" />
            {b.beacon_id}
          </span>
          <span style={{ color: "#8b949e" }}>
            {b.rssi != null ? `${b.rssi.toFixed(0)} dBm` : "—"} · hop {b.hop_count ?? "?"}
          </span>
        </div>
      ))}
    </div>
  );
}