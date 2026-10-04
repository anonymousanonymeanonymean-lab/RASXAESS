# ONA ↔ COMMAND POST — Integration Contract v1.0

## Broker
- MQTT over TLS (port 8883 par défaut)
- Auth : username/password ou certificats

## Topics SUBSCRIBE (par le Command Post)
ona/v1/{mission_id}/events      QoS 1
ona/v1/{mission_id}/positions   QoS 1
ona/v1/{mission_id}/telemetry   QoS 0
ona/v1/{mission_id}/alerts      QoS 1
ona/v1/{mission_id}/status      QoS 1 retained
ona/v1/{mission_id}/devices     QoS 1 retained

## Topics PUBLISH (par le Command Post)
ona/v1/{mission_id}/ack         QoS 1
ona/v1/{mission_id}/commands    QoS 1

## Payload — Event (schéma minimal)
{
  "message_id": "uuid",
  "mission_id": "mission_default",
  "source_id": "BEACON_03",
  "source_type": "BEACON",
  "message_type": "EVENT",
  "boot_id": "a3f9",
  "sequence_number": 245,
  "event_timestamp": "2026-10-04T12:34:56Z",
  "received_timestamp": "2026-10-04T12:34:57Z",
  "frame_id": "FRAME_LOCAL_01",
  "coordinate_reference": "ENU",
  "local_x": 12.5, "local_y": -3.2, "local_z": 0.0,
  "latitude": null, "longitude": null, "altitude": null,
  "event_type": "GAS",
  "severity": "HIGH",
  "confidence": 0.94,
  "priority": "CRITICAL",
  "payload": {}
}

## Payload — ACK (Command Post → ONA)
{
  "ack_message_id": "uuid",
  "ack_status": "RECEIVED",
  "ack_timestamp": "2026-10-04T12:34:58Z"
}