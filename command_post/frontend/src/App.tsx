import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "./api";
import { connectWS } from "./ws";
import type { AlertData, BeaconData, EventData, RobotData } from "./types";
import TopBar from "./components/TopBar";
import RobotPanel from "./components/RobotPanel";
import BeaconPanel from "./components/BeaconPanel";
import AlertPanel from "./components/AlertPanel";
import EventPanel from "./components/EventPanel";
import CommsMonitor from "./components/CommsMonitor";
import EventDetailsDrawer from "./components/EventDetailsDrawer";
import LivingMap from "./map/LivingMap";

export default function App() {
  const [events, setEvents] = useState<EventData[]>([]);
  const [robots, setRobots] = useState<RobotData[]>([]);
  const [beacons, setBeacons] = useState<BeaconData[]>([]);
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [selected, setSelected] = useState<EventData | null>(null);
  const [mqttOk, setMqttOk] = useState(false);
  const [lastMsg, setLastMsg] = useState<string>("—");

  const eventsRef = useRef<EventData[]>([]);
  eventsRef.current = events;

  // Initial load
  useEffect(() => {
    api.events().then(setEvents).catch(console.warn);
    api.robots().then(setRobots).catch(console.warn);
    api.beacons().then(setBeacons).catch(console.warn);
    api.alerts().then(setAlerts).catch(console.warn);
    const t = setInterval(async () => {
      try {
        const h = await api.health();
        setMqttOk(h.mqtt_connected);
      } catch {}
    }, 5000);
    return () => clearInterval(t);
  }, []);

  // WebSocket
  useEffect(() => {
    const close = connectWS((msg) => {
      setLastMsg(new Date().toISOString());
      switch (msg.kind) {
        case "NEW_EVENT": {
          const e = msg.data as EventData;
          setEvents((prev) => {
            const others = prev.filter((x) => x.event_id !== e.event_id);
            return [e, ...others];
          });
          break;
        }
        case "EVENT_UPDATED": {
          const e = msg.data as EventData;
          setEvents((prev) =>
            prev.map((x) => (x.event_id === e.event_id ? e : x)),
          );
          break;
        }
        case "ROBOT_UPDATED": {
          const r = msg.data as RobotData;
          setRobots((prev) => {
            const others = prev.filter((x) => x.robot_id !== r.robot_id);
            return [r, ...others];
          });
          break;
        }
        case "BEACON_UPDATED": {
          const b = msg.data as BeaconData;
          setBeacons((prev) => {
            const others = prev.filter((x) => x.beacon_id !== b.beacon_id);
            return [b, ...others];
          });
          break;
        }
        case "ALERT_CREATED": {
          const a = msg.data as AlertData;
          setAlerts((prev) => [a, ...prev]);
          break;
        }
      }
    });
    return close;
  }, []);

  // Local recompute of aging every 5s (keeps UI fresh)
  useEffect(() => {
    const t = setInterval(() => {
      setEvents((prev) =>
        prev.map((e) => {
          const age = (Date.now() - new Date(e.event_timestamp).getTime()) / 1000;
          let status: EventData["status"] = "ACTIVE";
          if (age <= 10) status = "NEW";
          else if (age <= 60) status = "ACTIVE";
          else if (age <= 300) status = "RECENT";
          else if (age <= 900) status = "STALE";
          else status = "EXPIRED";
          return { ...e, age_seconds: age, status };
        }),
      );
    }, 5000);
    return () => clearInterval(t);
  }, []);

  const onSelect = (e: EventData) => setSelected(e);

  const onAckAlert = async (id: string) => {
    const r = (await api.ackAlert(id)) as AlertData;
    setAlerts((prev) => prev.map((a) => (a.alert_id === r.alert_id ? r : a)));
  };
  const onResolveAlert = async (id: string) => {
    const r = (await api.resolveAlert(id)) as AlertData;
    setAlerts((prev) => prev.map((a) => (a.alert_id === r.alert_id ? r : a)));
  };

  const missionId = useMemo(
    () => events[0]?.mission_id ?? "mission_default",
    [events],
  );

  return (
    <div className="layout">
      <div className="topbar">
        <span className="title">THE LIVING MAP — COMMAND POST</span>
        <span>
          MISSION: <b>{missionId}</b>{" "}
          <span className={`status-dot ${mqttOk ? "dot-ok" : "dot-danger"}`} />
          <span style={{ color: "#8b949e" }}>{mqttOk ? "MQTT ONLINE" : "MQTT OFFLINE"}</span>
        </span>
      </div>

      <div className="card panel-left">
        <RobotPanel robots={robots} />
        <div style={{ height: 12 }} />
        <BeaconPanel beacons={beacons} />
      </div>

      <div className="card panel-map">
        <LivingMap
          events={events}
          robots={robots}
          beacons={beacons}
          onSelect={onSelect}
          selectedId={selected?.event_id}
        />
      </div>

      <div className="card panel-right">
        <AlertPanel
          alerts={alerts}
          onAck={onAckAlert}
          onResolve={onResolveAlert}
        />
        <div style={{ height: 12 }} />
        <CommsMonitor
          mqttOk={mqttOk}
          lastMsg={lastMsg}
          robots={robots}
          beacons={beacons}
          events={events}
        />
      </div>

      <div className="card panel-detail">
        <EventDetailsDrawer event={selected} />
      </div>
    </div>
  );
}