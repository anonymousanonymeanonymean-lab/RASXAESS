export default function TopBar({ missionId, mqttOk }: { missionId: string; mqttOk: boolean }) {
  return (
    <div className="topbar">
      <span className="title">THE LIVING MAP</span>
      <span>
        MISSION: <b>{missionId}</b>{" "}
        <span className={`status-dot ${mqttOk ? "dot-ok" : "dot-danger"}`} />
        {mqttOk ? "MQTT ONLINE" : "MQTT OFFLINE"}
      </span>
    </div>
  );
}