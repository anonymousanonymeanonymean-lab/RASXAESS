# FAILURE CASES

This document outlines the potential failure cases, their mitigations, and the planned verification tests as defined in the system architecture for "The Living Map".

| Failure | Mitigation | Planned test / Expected result |
| :--- | :--- | :--- |
| **Packet loss, lost ACK** | ACK and retry | Message delivered after retransmission |
| **Duplicate packet** | Deduplication on source ID, boot ID and sequence | Processed only once |
| **Corrupted frame** | CRC-16 check | Invalid frame rejected |
| **Relay beacon failure** | Parent reselection, route recovery, store-and-forward | Message delivered through another route |
| **ONA or uplink down** | SQLite storage, PENDING outbox, automatic resend | Data sent after reconnection |
| **Beacon reboot** | Boot ID and sequence recovery | No duplicate, order recovered |
| **False detection, stale data** | Confidence score; records marked stale after validity | Low-confidence event not dispatched |
| **Robot blocked, low battery** | Return threshold, re-planning, mission reissued | Mission continues after recovery |