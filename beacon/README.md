# BEACON — The Memory of the Living Map

**TSYP14 Technical Challenge — "The Living Map: Spatial Memory for Emergency Robots"**
IEEE RAS × IEEE AESS Tunisia Section Chapters

This document explains the **concept** of the beacon: why it exists, what it does, how it works with the rest of the system, and how it behaves in our earthquake scenario. It contains no code.

---

## Table of Contents

1. [The Problem Beacons Solve](#1-the-problem-beacons-solve)
2. [The Idea](#2-the-idea)
3. [Where Beacons Fit in the System](#3-where-beacons-fit-in-the-system)
4. [The Life of a Beacon](#4-the-life-of-a-beacon)
5. [What a Beacon Remembers](#5-what-a-beacon-remembers)
6. [How Beacons Talk](#6-how-beacons-talk)
7. [How Beacons Relay Data to the Outside](#7-how-beacons-relay-data-to-the-outside)
8. [How the Executor Uses Beacons](#8-how-the-executor-uses-beacons)
9. [Information Aging](#9-information-aging)
10. [Where to Drop Beacons](#10-where-to-drop-beacons)
11. [Our Scenario: The Earthquake](#11-our-scenario-the-earthquake)
12. [What Can Go Wrong, and How Beacons Cope](#12-what-can-go-wrong-and-how-beacons-cope)
13. [Why These Technology Choices](#13-why-these-technology-choices)
14. [Rules Beacons Respect](#15-rules-beacons-respect)
15. [Glossary](#16-glossary)

---

## 1. The Problem Beacons Solve

After an earthquake, rescue robots enter buildings where **GPS does not work** and **no phone or data network exists**. The first robot explores and finds important things: a trapped worker, a toxic gas leak, a blocked corridor.

But if that robot breaks, runs out of battery, or simply leaves, **everything it learned disappears with it**. The next robot starts from zero, wasting precious time while people are in danger.

The challenge asks for a system that can:

> **Sense → Communicate → Preserve critical information → Enable mission continuity**

Beacons are the "preserve" and "continuity" part.

---

## 2. The Idea

**Instead of keeping knowledge inside the robot, leave it inside the building.**

While the **Writer** robot explores, it drops small radio devices, the **beacons**, on the floor. Each beacon holds a short note about what is happening around it. Together, the beacons form a **trail** from the entrance to every important place.

The building gets **its own memory**:

- The robot can leave, fail or be replaced. The memory stays.
- A second robot (the **Executor**) can arrive later, and go straight to the problem.
- Beacons also pass the information outward, so people outside know what is inside.

It is the same idea as leaving a trail of notes in a cave, except that the notes can talk to each other by radio.

---

## 3. Where Beacons Fit in the System

| Actor | Role | Relation to beacons |
|---|---|---|
| **Writer robot** | Explores the building, detects events | **Drops** beacons| The beacon **writes** information through algorithms, Store and relay information | The **memory and the radio chain** |
| **ONA** (Outside Network Area) | Bridge between the building and the outside world | **Receives** the information coming out of the beacon chain |
| **Command Post** | Remote decision center with the live map | Never talks to beacons directly |
| **Executor robot** | Intervenes (clears debris, brings an oxygen mask, filters gas) | **gets Commands** from the Command Post |

The flow in plain words:

> Writer explores → drops beacons → beacons write events and pass the information toward the exit → the ONA receives, converts positions to real GPS and sends it to the Command Post → the commander decides → the ONA briefs the Executor → the Executor enters and follows the beacons.

**Fundamental rule:** there is **no direct link** between a beacon (or any robot) and the Command Post. Everything passes through the ONA.

---

## 4. The Life of a Beacon

| Phase | What happens |
|---|---|
| **1. Prepared** | Before the mission, each beacon receives a unique identity and the mission it belongs to. It is loaded onto the Writer. |
| **2. Dropped** | The Writer puts the beacon on the floor at a chosen spot and writes the first information: its position and its place in the chain. |
| **3. Alive** | The beacon announces itself regularly so neighbors know it is there, and it listens for messages. |
| **4. Remembering** | If an event is found nearby, the Writer writes it into the beacon: what, where, when. |
| **5. Relaying** | The beacon passes messages along the chain toward the exit and acknowledges what it receives. |
| **6. Waiting** | If the next beacon is unreachable, the beacon keeps the message and tries again later. |
| **7. Read** | The Executor passes close to it, reads what it knows and moves on to the next one. |

---

## 5. What a Beacon Remembers

The challenge says a beacon message must tell **what was found, where to go, and when it was written**.

| Question | Meaning | Example |
|---|---|---|
| **What?** | The type of event | A trapped worker, a toxic gas leak |
| **How serious?** | Urgency or intensity | Critical, high gas concentration |
| **Where?** | Position relative to the beacon, in the Writer's own coordinate system | A few meters ahead on the left |
| **Where to go?** | Which beacon comes next on the way to the event, and in which direction | "Next is beacon 4, 8 meters ahead" |
| **When?** | The moment the information was written | Minutes after the mission started |
| **How reliable?** | Confidence in the detection | Confirmed by two sensors |

Beacons also carry **housekeeping information**: who they are, which mission they belong to, their battery state and how many messages they are holding.

Messages are kept **short on purpose**: short messages travel farther on radio, use less battery, and are less likely to be lost.

---

## 6. How Beacons Talk

### Radio, not network

Beacons use **long-range, low-power radio (LoRa)**. It passes through walls and debris better than ordinary radio and needs very little energy. It requires no infrastructure, so it keeps working when the cell tower is destroyed.

### Kinds of conversation

| Conversation | Purpose |
|---|---|
| **Presence** | "I am here and healthy." Sent regularly so neighbors know who is alive. |
| **Status** | Battery level, stored messages, link quality. |
| **Event** | "Something important was found near me." This is the mission data. |
| **Forwarding** | "Please pass this message toward the exit." |
| **Acknowledgment** | "Message received." Confirms delivery from one beacon to the next, and from the ONA back to the origin. |
| **Routing** | "Which way is the exit?" Beacons help each other find the path outward. |

### Priorities

Not all messages are equal. A life-threatening event goes before a routine status message.

| Priority | Typical use |
|---|---|
| Low | Heartbeats, status |
| Normal | Routing exchanges |
| High | Events |
| Critical | A trapped person, a dangerous gas level |

### Trust and uniqueness

- Every message carries a **check value**, so a corrupted message is detected and thrown away.
- Every message has a **unique identity** (who sent it, which start-up, which number), so a beacon never forwards the same message twice.
- A **version number** ensures that devices running different rules ignore each other instead of misunderstanding.

---

## 7. How Beacons Relay Data to the Outside

A single radio link cannot cross a whole factory, so data **hops** from beacon to beacon.

| Concept | Explanation |
|---|---|
| **Multi-hop** | A message travels through several beacons: B6 → B5 → B4 → … → B1 → ONA. |
| **Hop limit** | Each message may only travel a limited number of hops, so it never circulates forever. |
| **Neighbor awareness** | Each beacon knows which others it can hear and how good the link is. |
| **Next-hop choice** | The beacon picks the neighbor that leads toward the ONA with the best link. |
| **Store-and-forward** | If no neighbor is reachable, the beacon **keeps** the message and sends it as soon as a neighbor reappears. Critical messages are sent first. |
| **Survival** | Stored messages are written to the beacon's memory, so they survive a restart. |

Think of it as a **relay race**: each beacon passes the baton to the next one and makes sure it was received before letting go.

---

## 8. How the Executor Uses Beacons

The Executor does not explore. It **follows an existing trail**.

1. **Briefing (outside):** the ONA tells the Executor where the events are, which beacons lead there, and what hazards exist.
2. **Entering:** the Executor hears the first beacon of the chain.
3. **Following:** each beacon tells it which beacon is next, in which direction, and how far. The strength of the radio signal helps it get closer.
4. **Checking:** at the destination, it compares what the beacons said with what it sees. Old information must be verified.
5. **Acting:** clears debris and delivers an oxygen mask (trapped worker), or inspects and filters the air (gas leak).
6. **Reporting:** the result goes back out through the ONA to the live map.

Because the beacons carry the route, the Executor works even if it has **no map, no GPS and no contact with the outside** once inside.

---

## 9. Information Aging

In a disaster, the situation changes: a gas leak may grow or fade; a victim's condition may worsen; a corridor may collapse further.

So every piece of information has a **written-at moment** and a **validity period**.

| Information age | How it is treated |
|---|---|
| **Fresh** | Trusted, acted on directly. |
| **Getting old** | Still useful, but its reliability is reduced. |
| **Expired** | Treated as a hint only, must be **re-verified** by the Executor on the spot. |

This prevents a robot from acting blindly on outdated data.

---

## 10. Where to Drop Beacons

The Writer decides when to deposit a beacon. Four reasons:

| Trigger | Why |
|---|---|
| **Distance** | Roughly every 10 meters, always below the radio range with a safety margin, so each beacon can hear its neighbors. |
| **Event** | Whenever an event is confirmed, a beacon is placed right there so the event is anchored to a device. |
| **Junction** | At crossings and major turns, so the Executor does not take the wrong path. |
| **Weak link** | If the signal to the previous beacon becomes weak (thick walls, metal), drop earlier to avoid a gap. |

**The trade-off:** more beacons make the chain stronger but use up the Writer's stock and time; fewer beacons reach farther but risk gaps. Finding the right spacing, based on real radio range inside the facility, is one of the studies of the project.

---

## 11. Our Scenario: The Earthquake

**Setting:** an industrial facility damaged by an earthquake. The telecom tower (BTS) is destroyed. No GPS indoors. Several emergencies at once.

### Event 1 — Trapped worker

1. The Writer detects a person under collapsed wall debris.
2. A beacon is dropped next to the spot and records: trapped person, critical, position, route back to the entrance, time.
3. The information moves along the chain to the ONA, then to the Command Post.
4. The Executor is sent. It follows the beacons, clears the debris and gives the worker an oxygen mask so he can breathe.

### Event 2 — Toxic gas leak

1. The Writer's gas sensor detects a leak from a damaged pipeline.
2. A beacon records the gas event, its level and where it is strongest.
3. Same path to the outside: ONA, then Command Post.
4. The Executor goes to the area, inspects it and filters the gas.

Both events use the **same beacon trail**. That is the strength of the design: one memory, many missions.

---

## 12. What Can Go Wrong, and How Beacons Cope

| Failure | Consequence | Protection |
|---|---|---|
| **The Writer dies before leaving** | Its knowledge would be lost | The knowledge is already in the beacons. |
| **A beacon is crushed or runs out of battery** | A hole in the chain | Beacons overlap in range, and a message can skip one missing beacon. |
| **Radio range is shorter than expected** | Chain broken | Extra beacon when the signal weakens; range tested beforehand. |
| **The Writer's position estimate drifts** | Events slightly misplaced | Beacons store relative directions and distances, so local navigation still works. |
| **Data becomes outdated** | Executor acts on old information | Aging: old data must be re-verified. |
| **Message corrupted or duplicated** | Wrong decisions | Check value and unique identity on every message. |
| **No neighbor reachable** | Data stuck | Store-and-forward: keep and retry. |
| **Link to the Command Post is lost** | Operators blind | The ONA holds data and retries (its own responsibility). |
| **Radio interference or identity clash** | Mixed-up chain | Unique identities per beacon, timing variation between transmissions. |

---

## 13. Why These Technology Choices

| Choice | Reason |
|---|---|
| **LoRa radio** | Long range, passes through obstacles, very low power, needs no infrastructure. |
| **SX1262 transceiver** | Efficient LoRa chip with good sensitivity, supported by a mature software library. |
| **ESP32 microcontroller** | Inexpensive, enough memory for storage and routing, low-power modes, widely available. |
| **Compact binary messages** | Shorter radio time, longer range, less battery. |
| **Store-and-forward memory** | Survives reboots and temporary disconnections. |
| **Check value on every message** | Radio is noisy in a damaged building. |

---


**Today:** a beacon starts up, checks itself, announces its presence regularly and listens to the other beacons, with signal strength and quality measured on each message.

**Known gaps to close before integration:**
- The configuration file of the project (identity, radio settings, wiring) is still empty and must be filled in.
- The time stamp currently counts from the beacon's own start-up, so it cannot yet be compared between devices. A shared mission clock is needed for aging to work.
- The restart identifier is not random enough.
- Power saving is not yet implemented, and beacons must last the whole mission.

---

## 14. Rules Beacons Respect

-  Messages are compact.
-  Communication is by radio broadcast.
-  Messages are protected against corruption and duplication.
-  No direct link to the Command Post; everything exits through the ONA.
-  Messages carry what / where / when (step 7).
-  Information aging (step 7).

---

## 15. Glossary

| Term | Meaning |
|---|---|
| **Beacon** | Small radio node dropped on the floor; the building's memory |
| **Writer** | Robot that explores and writes information into beacons |
| **Executor** | Robot that reads the beacons and intervenes |
| **ONA** | Outside Network Area; the bridge between the disconnected zone and the outside world |
| **Command Post** | Remote center with the live map where the commander decides |
| **BTS** | Cell tower, destroyed in our scenario |
| **GPS-denied** | A place where satellite positioning does not work |
| **Multi-hop** | Passing a message through several devices to reach a distant target |
| **Store-and-forward** | Keeping a message until it can be passed on |
| **Signal strength** | How strongly a radio message is received; used to estimate proximity |
| **Aging** | Reducing trust in information as it gets older |

---

# run the beacon 
Requirements: PlatformIO (VS Code extension or CLI), an ESP32 board with an SX1262 LoRa module, and a USB data cable.

⚠️ Fill src/config.h first (beacon id, mission id, LoRa pins and radio settings). It is empty in the repository, so the build fails without it. Connect the antenna before powering the radio.

Install PlatformIO (CLI):


pip install platformio

## Build, flash and open the serial monitor:


cd beacon
pio run -e esp32dev                # build
pio run -e esp32dev -t upload      # flash
pio device monitor                 # serial monitor, 115200 baud

Use -e esp32s3 for the ESP32-S3 target.

## Find and select the serial port:


pio device list
pio run -e esp32dev -t upload --upload-port COM3
pio device monitor --port COM3

Test two beacons: set a different BEACON_ID in config.h for each board, flash both, and open a monitor on each. Every board should print RX: lines with RSSI and SNR for the other one's HELLO.

Clean the build:


pio run -t clean
