export interface EventData {
  event_id: string;
  mission_id: string;
  source_id: string;
  source_type: string;
  event_type: string;
  event_timestamp: string;
  received_timestamp: string;
  age_seconds: number;
  status: "NEW" | "ACTIVE" | "RECENT" | "STALE" | "EXPIRED";
  frame_id: string | null;
  coordinate_reference: string;
  local_x: number | null;
  local_y: number | null;
  local_z: number | null;
  latitude: number | null;
  longitude: number | null;
  altitude: number | null;
  severity: string;
  confidence: number;
  priority: string;
  payload: Record<string, unknown>;
}

export interface RobotData {
  robot_id: string;
  robot_type: string;
  status: string;
  frame_id: string | null;
  local_x: number | null;
  local_y: number | null;
  local_z: number | null;
  latitude: number | null;
  longitude: number | null;
  battery: number | null;
  last_seen: string;
  communication_status: string;
}

export interface BeaconData {
  beacon_id: string;
  status: string;
  frame_id: string | null;
  local_x: number | null;
  local_y: number | null;
  local_z: number | null;
  battery: number | null;
  hop_count: number | null;
  parent_id: string | null;
  rssi: number | null;
  snr: number | null;
  last_seen: string;
}

export interface AlertData {
  alert_id: string;
  mission_id: string;
  event_id: string | null;
  severity: string;
  message: string;
  status: string;
  created_at: string;
}

export interface WsMessage {
  kind: string;
  data: unknown;
}