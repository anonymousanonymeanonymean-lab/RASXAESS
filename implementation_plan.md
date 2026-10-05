# THE LIVING MAP: SPATIAL MEMORY FOR EMERGENCY ROBOTS
## PHASE 1 - IMPLEMENTATION PLAN
*Challenge proposed by IEEE RAS and IEEE AESS Tunisia | October 2026*

---

## 1. Approach

**Guiding rule:** Build the minimum functional system first, then make it better. The target is a system that is simple, reliable, modular, testable, and demonstrable.

### Workflow
`RESEARCH` $\rightarrow$ `SIMULATE` $\rightarrow$ `DEVELOP` $\rightarrow$ `TEST` $\rightarrow$ `INTEGRATE` $\rightarrow$ `BREAK` $\rightarrow$ `IMPROVE` $\rightarrow$ `DEMONSTRATE`

### Parallel Development
All groups work at the same time and respect common interfaces, so that no group waits for another:

* **Navigation** $\rightarrow$ Robot State
* **Perception** $\rightarrow$ Event
* **Beacon** $\rightarrow$ Beacon Packet
* **ONA** $\rightarrow$ Translated Data
* **Command Post** $\rightarrow$ Mission
* **Executor** $\rightarrow$ Mission Execution

Each module defines its inputs, outputs, data format, protocol, and error conditions, develops a minimal working version, tests it alone, documents it, and then delivers a stable version for integration.

### Three Development Levels

1. **Level 1: Simulation**
   Virtual Writer $\rightarrow$ Virtual event $\rightarrow$ Virtual beacon $\rightarrow$ Virtual gateway $\rightarrow$ Command Post $\rightarrow$ Virtual Executor. Validates the whole logic before any hardware is used.
2. **Level 2: Hardware-in-the-loop**
   Real sensors, ESP32 microcontrollers, LoRa radios, beacons, and ONA are connected progressively.
3. **Level 3: Complete Prototype**
   Writer robot $\rightarrow$ Beacons $\rightarrow$ ONA $\rightarrow$ Command Post $\rightarrow$ Executor robot.

---

## 2. Work Organisation

Four technical groups and one central team:

* **Robotics & Autonomy:** Writer and Executor robots, autonomous navigation, motor control, obstacle avoidance, localisation, robot sensors.
* **Perception & Spatial Memory:** Event detection and classification, event position estimate, beacons, spatial memory, data format.
* **Communication & ONA:** Robot-beacon and beacon-gateway communication, gateway, Outside Network Area, transmission to the Command Post, communication reliability.
* **Command Post & Living Map:** Coordinate translation, mapping, database, dashboard, mission generation, link to the Executor.
* **Core Team:** Global architecture, interfaces, GitHub, integration, system tests, versions, technical documentation, final validation.

> **Note:** For each critical feature, there is one Responsible and one Backup, so that no important feature depends on a single person.

---

## 3. Timeline

* **Sprint 0 launched:** 10/09/2026.
* **Sprints 1–10 dates:** Fixed after the Sprint 0 review, when research results, available resources, and the real state of each group are known.
* **First challenge deadline:** 5 October 2026.
* **Final submission:** 1 December 2026.

### Sprint Structure
`Sprint planning` $\rightarrow$ `Parallel work` $\rightarrow$ `Mid-sprint technical check` $\rightarrow$ `Integration and testing` $\rightarrow$ `Sprint review` $\rightarrow$ `Decision (GO / ADJUST / REDO)`

---

## 4. Sprint Plan

| Sprint | Goal | Expected Result |
| :--- | :--- | :--- |
| **S0** | Kick-off and research | Research documents, event list, protocol proposal, dashboard mock-up, architecture V1, interface document V1, backlog |
| **S1** | Architecture and proof of concept | Basic navigation prototype in simulation, Event and Beacon models, first simulated data exchange, Living Map V1, architecture V2 |
| **S2** | Writer robot and event detection | Writer explores, detects, generates an event and sends the data |
| **S3** | Beacon and spatial memory | Detect, decide, deploy a beacon and store the critical information |
| **S4** | ONA and data transmission | Robot $\rightarrow$ RF $\rightarrow$ Gateway $\rightarrow$ ONA $\rightarrow$ Internet $\rightarrow$ Command Post, tested against loss and delay |
| **S5** | Coordinate translation and Living Map | Local robot data $\rightarrow$ coordinate translation $\rightarrow$ Living Map |
| **S6** | Executor robot | Executor receives a mission, retrieves the beacon memory and continues the mission |
| **S7** | Full system integration | Complete scenario (Section 6) |
| **S8** | Failure testing and robustness | `FAIL` $\rightarrow$ `DETECT` $\rightarrow$ `RECOVER` $\rightarrow$ `CONTINUE MISSION` (see `FAILURE_CASES.txt`) |
| **S9** | Optimisation and innovation | Improvements on a stable system only |
| **S10** | Final demo and pitch | Prototype, GitHub, final architecture, user manual, 5-minute pitch |

### Details per Sprint

* **S0 - Kick-off and research:** Each group studies the problem and existing solutions (navigation methods and sensors; event detection, beacon technologies and spatial memory; RF technologies, protocols and gateways, with range, latency and reliability constraints; mapping and supervision interfaces and coordinate transformation). The Core Team compares the proposals and identifies the mandatory requirements, the interfaces, and the major risks.
* **S1 - Architecture and proof of concept:**
  * *Robotics:* Robot software architecture, Writer and Executor models, motor and sensor tests in simulation, movement commands.
  * *Perception:* First detection system, Event model, Beacon model, simulated beacon creation.
  * *Communication:* Protocol, Beacon Packet, simulated robot-to-gateway exchange, first ONA version.
  * *Command Post:* Database structure, first interface showing a robot, an event, and a beacon.
  * *Core Team:* Final interfaces, GitHub repositories, code conventions, data structures.
* **S2 - Writer robot and event detection:** Navigation, obstacle avoidance, exploration, position management, battery management; event detection, classification, position estimate, event ID and Event Packet; transmission of events; reception and display of events and positions at the Command Post, with event history.
* **S3 - Beacon and spatial memory:** Rule for when the Writer drops a beacon, recording of its position and continuation of the exploration; beacon content, Beacon-Event association, timestamp, priority and validity of the information; beacon identification, range test and message handling; display of beacons and of the spatial memory.
* **S4 - ONA and data transmission:** Chain: Robot $\rightarrow$ RF $\rightarrow$ Gateway $\rightarrow$ ONA $\rightarrow$ wireless/Internet $\rightarrow$ Command Post. Tests: connection loss, reconnection, incomplete messages, transmission delay, duplicated messages. End-to-end test and measurement of reliability.
* **S5 - Coordinate translation and Living Map:** The Writer provides local coordinates and orientation; the ONA transports the position information without modification and guarantees its integrity; the Command Post performs the local-to-global translation and shows events, beacons, robots, dangerous zones and the mission history. Transformations are tested with several positions.
* **S6 - Executor robot:** Executor navigation, beacon detection, navigation to a beacon and mission following; reading of beacon information and identification of the critical event; mission generation, selection of the intervention zone and sending of the mission through the ONA.
* **S7 - Full system integration:** All groups work together on integration, bug fixing, data synchronisation, interface tests, and reliability.
* **S8 - Failure testing and robustness:** Each group defines and runs its own failure cases (see `FAILURE_CASES.txt`).
* **S9 - Optimisation and innovation:** Possible axes: autonomy, decision intelligence, communication optimisation, smart beacon management, visualisation, prediction, event prioritisation, smart spatial memory management, energy optimisation. *Rule: innovation comes after stability. A reliable function is never sacrificed for a complex but unstable one.*
* **S10 - Final demo and pitch:** Robot calibration and repeated tests, validation of events and beacons, full communication test and backup scenarios, final dashboard, documentation, GitHub, final architecture, user manual, 5-minute pitch, and preparation of the answers to questions.

---

## 5. Phase 1 Prototype Scope

| Element | Phase 1 Implementation |
| :--- | :--- |
| **Writer robot** | ESP32 (WROOM) with 3 ultrasonic sensors, gyroscope, gas sensor and 4 motors; Raspberry Pi with camera, 2 microphones and NLP detection of the word *"aide"*; serial link (UART or USB) between the two boards; LoRa interface |
| **Beacon** | ESP32 + SX1262 LoRa module, antenna, battery, power regulation, deployment switch *(final version: custom PCB, ESP32-S3, rugged enclosure)* |
| **ONA** | Existing PC, ESP32 + LoRa radio on USB/UART (or simulated radio), Python (ROS 2 optional), SQLite, Wi-Fi/4G uplink |
| **Command Post** | Web dashboard (Living Map), Python/FastAPI backend, MQTT over TLS, SQLite *(PostgreSQL/PostGIS later)* |
| **Executor robot** | Beacon-guided navigation, debris removal, oxygen mask and medical kit, gas filtering unit |

> **Note:** The PC is a development platform: the final ONA can move to a Raspberry Pi or a rugged embedded computer without changing the logical architecture.

---

## 6. Full Integration Scenario (Sprint 7 / Final Demonstration)

1. The **Writer** starts and explores.
2. The **Writer** detects an event and creates an Event.
3. The **Writer** drops a beacon and writes the event into it.
4. The **beacon** keeps the critical information and transmits it (direct or multi-hop) to the ONA.
5. The **ONA** receives, validates, stores, and forwards the information.
6. The **Command Post** receives the data and the Living Map updates automatically.
7. The **operator** sees source, time, position, confidence, and status; event aging changes its status.
8. A **mission** is generated and sent through the ONA to the Executor.
9. The **Executor** enters the environment, detects the beacon, and retrieves the information.
10. The **Executor** continues and completes the mission.

---

## 7. Deliverables Checklist

- [ ] GitHub repository
- [ ] Simulation demo
- [ ] Short technical report (maximum 6 pages)
- [ ] Implementation plan (this document)
- [ ] Failure cases (`FAILURE_CASES.txt`)
- [ ] Technical solution and architecture (`TECHNICAL_SOLUTION_AND_ARCHITECTURE.txt`)