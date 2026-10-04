import type { BeaconData, EventData, RobotData } from "../types";

export default function CommsMonitor({
  mqttOk,
  lastMsg,
  robots,
  beacons,
  events,
}: {
  mqttOk: boolean;
  lastMsg: string;
  robots: RobotData[];
  beacons: BeaconData[];
  events: EventData[];
}) {
  const writer = robots.find((r) => r.robot_type === "WRITER");
  const executor = robots.find((r) => r.robot_type === "EXECUTOR");
  return (
    <div>
      <h3>COMMS MONITOR</h3>
      <div className="row">
        <span>MQTT</span>
        <span>
          <span className={`status-dot ${mqttOk ? "dot-ok" : "dot-danger"}`} />
          {mqttOk ? "CONNECTED" : "DISCONNECTED"}
        </span>
      </div>
      <div className="row">
        <span>Last event</span>
        <span style={{ color: "#8b949e" }}>{lastMsg}</span>
      </div>
      <div className="row">
        <span>Beacons</span>
        <span>{beacons.length}</span>
      </div>
      <div className="row">
        <span>Writer</span>
        <span>{writer?.status ?? "—"}</span>
      </div>
      <div className="row">
        <span>Executor</span>
        <span>{executor?.status ?? "—"}</span>
      </div>
      <div className="row">
        <span>Events total</span>
        <span>{events.length}</span>
      </div>
    </div>
  );
}