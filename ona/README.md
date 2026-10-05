# 🔷 ONA — Outside Network Area

**The Living Map: Spatial Memory for Emergency Robots**
TSYP14 Technical Challenge · IEEE RAS × IEEE AESS — Tunisia Section Chapters

---

## The Idea in One Paragraph

After a disaster, a building can become a place where nothing connects to anything: no GPS, no phone network, no radio reaching the outside. A first robot, the **Writer**, can go in and discover what is happening, but what it learns is worthless if it stays trapped inside the robot or inside the building. The **Outside Network Area (ONA)** is the missing bridge. It is a small station set up just outside the dead zone that takes what the Writer found, makes sense of it, ties it to the real world, sends it to the people in charge, and prepares the second robot, the **Executor**, so it never has to start from zero.

> **The ONA gives the building a voice.** The beacons give it a memory; the ONA makes that memory useful to the outside world.

---

## 1. The Problem the ONA Solves

Inside a damaged industrial building, three things are broken at once:

| What is broken | Consequence |
|---|---|
| **No GPS** | Robots only know where they are relative to where they started. Their coordinates mean nothing to anyone else. |
| **No network** | The telecom tower is down. Nothing inside can call out. |
| **Radio stops at the wall** | Even the robots' own radios cannot reach the command post from deep inside. |

And a fourth problem sits on top: **robots fail.** A Writer can run out of battery, get damaged, or be lost. If knowledge only lives in the robot, it dies with it.

So there is a gap between **where the knowledge is created** (inside) and **where decisions are made** (outside, far away). The ONA exists to close that gap, and it is the **only** way across it.

---

## 2. Where the ONA Sits

```
   INSIDE THE BUILDING          │        OUTSIDE NETWORK AREA          │      FAR AWAY
   no GPS · no network          │                                      │
                                │                                      │
   Writer robot  ───────────────┼──▶  Receive → Translate → Carry ─────┼──▶  Command Post
   Beacons on the floor         │                  │                   │     (live map,
                                │                  └─ Brief ───────────┼──▶  commander decides)
                                │                         │            │
                         radio stops here                 ▼
                                                    Executor robot
                                                  (waiting to be briefed)
```

The ONA stands just beyond the point where radio stops. It faces two ways: toward the dead zone, where it collects information, and toward the outside world, where it delivers it.

**A rule that defines the whole design:** *no robot may talk directly to the command post.* Everything between inside and outside passes through the ONA. This is not a limitation. It is what makes the ONA a real gateway rather than an optional relay.

---

## 3. The Four Roles

The ONA does four jobs. Together they turn "a robot came back with some data" into "the right people know what to do and the next robot is ready to go."

### Role 1 — RECEIVE
*Take in what the Writer produced.*

When the Writer returns from its exploration, it carries a record of what it found: **events** (a trapped worker, a toxic gas leak), the **beacons** it left behind, and its **private map frame**, which is the coordinate system it invented for itself during the mission. The ONA collects all of this.

Receiving is more than listening. The ONA must decide whether it can **trust** what it hears:
- Did the message arrive intact, or was it corrupted on the way?
- Does it come from a robot or beacon that belongs to this mission, or from something unknown?
- Have we already received this exact message? Radios repeat themselves, and the same event must not appear twice on the map.
- Is it still fresh? A gas cloud reported two hours ago may no longer exist.

Every message gets an explicit verdict. Nothing is quietly dropped or quietly accepted.

### Role 2 — TRANSLATE
*Convert private coordinates into a reference anyone can use.*

The Writer's coordinates are private: "12 metres forward and 4 metres left of where I started." That is meaningless to a command post hundreds of kilometres away, or to a second robot with its own starting point.

The ONA's translation role answers a simple question: **where, in the real world, is that?** It does this by anchoring the Writer's private frame to a known real-world point, such as the building entrance, which can be located precisely because it is *outside*, where GPS works. Once the frame is anchored, every point the Writer recorded can be expressed as a real-world position that **any agent can read and act on**.

Two principles matter here:

1. **Never invent a position.** If the ONA does not have a trustworthy connection between the Writer's frame and the real world, it keeps the coordinates local and says so honestly. A wrong location is worse than an honest "relative position only." In a rescue, a false location can send people to the wrong place.
2. **Be honest about precision.** A robot that has travelled far has accumulated some error in its sense of position. The ONA attaches an uncertainty to each position, so the commander sees a confidence area rather than a falsely exact dot.

### Role 3 — CARRY
*Reach the command post despite having no infrastructure.*

The command post is far away, and there is no phone network to rely on. The ONA must find its own way to deliver the information, using whatever long-range link is available, such as wireless or satellite.

Because that link may be unreliable, the ONA follows a **store-and-forward** approach:

- Everything received is **saved first**, before any attempt to send.
- Messages wait in a queue and are **retried** if the link is down, waiting longer between attempts rather than flooding a weak connection.
- **Urgent information goes first.** A trapped person outranks routine status updates when the link comes back.
- Messages that have waited too long are retired, because old information can mislead.

The result: **a dropped connection delays the information, but it never loses it.**

### Role 4 — BRIEF
*Prepare the mission plan the Executor needs before it enters.*

The whole point of the system is that the second robot **does not start from zero**. Before the Executor goes in, the ONA prepares and hands it a mission plan built from what the Writer discovered:

- **What was found**, meaning which events exist and what type each is.
- **Where they are**, in coordinates the Executor can use.
- **The route**, meaning the trail of beacons to follow from the entrance to each event.
- **How old each piece of information is**, so the Executor knows what to trust and what to re-check on arrival.
- **What to do**: free the trapped worker and give them an oxygen mask, or filter the toxic gas.

The briefing is the moment the Writer's discovery becomes the Executor's mission, which is the "mission continuity" the challenge asks for.

---

## 4. A Walk-Through: The Earthquake Scenario

An earthquake damages an industrial facility. The telecom tower fails. Two things happen inside:

- A wall section collapses and **traps a worker** under debris.
- A damaged pipeline starts releasing **toxic gas**.

**Step by step:**

1. **The Writer goes in.** It explores on its own, with no GPS, and detects both events. As it moves, it leaves small radio beacons on the floor, forming a trail and marking the events.
2. **The Writer comes back out** to the edge of the dead zone, carrying its findings.
3. **ONA — Receive.** The ONA accepts the findings, checking that each message is genuine, intact, new and not a repeat.
4. **ONA — Translate.** It anchors the Writer's private map to the real world, so the worker's location and the gas leak's location become real-world positions.
5. **ONA — Carry.** It sends the information to the command post, saving it first and retrying if the link drops. The trapped worker is flagged as the top priority.
6. **The command post** shows everything on a live map. The commander sees the events, where they are and how fresh the data is, and decides what to do.
7. **ONA — Brief.** The ONA prepares the mission plan and hands it to the Executor.
8. **The Executor enters** and follows the beacon trail. At the trapped worker it removes debris and provides an oxygen mask. At the leak it works to filter the gas.
9. **The map updates** as the mission completes, and the commander sees the events resolved.

At no point did the second robot have to explore. It arrived knowing.

---

## 5. Design Principles

| Principle | In plain words |
|---|---|
| **Single gateway** | The ONA is the only connection between inside and outside. No shortcuts. |
| **Trust before use** | Every message is checked, and every check gives a clear verdict. Nothing is silently accepted or silently discarded. |
| **Never invent a location** | If the real-world position can't be justified, it stays relative and the system says so. |
| **Save first, send later** | Information is stored before it is transmitted. A bad connection delays it but never destroys it. |
| **Most urgent first** | When bandwidth is scarce, a person in danger outranks routine updates. |
| **Information has an age** | Old data is marked as old. A hazard reported earlier may have changed. |
| **Independent of hardware** | The ONA thinks in terms of "a radio," not a specific device, so real hardware or a simulation can be swapped in. |
| **Independent of protocol** | Beacons and the Writer speak different "languages"; the ONA translates both into one common internal form. |

---

## 6. What the ONA Receives and Sends

**Coming in from the dead zone**
- From the **beacons**: short messages saying what was found, where to go, and when it was written.
- From the **Writer**: its events, its position updates, and the private frame it worked in.

**Going out to the command post**
- **Events**: what was found, of what type, how serious, how confident.
- **Positions**: where the Writer, beacons and events are.
- **Telemetry and status**: how the system itself is doing.
- **Alerts**: things the commander must see immediately.

**Going out to the Executor**
- The **mission briefing**: targets, route, coordinates, and the age of the information.

---

## 7. What Can Go Wrong, and How the Concept Handles It

| If this happens… | …the ONA's answer |
|---|---|
| The link to the command post goes down | Messages are saved and retried; urgent ones are sent first once the link returns |
| The ONA itself restarts | Everything saved is still there; delivery resumes |
| A message is corrupted in transit | It is rejected with a clear reason, never trusted |
| An unknown device sends data | It is rejected; only registered robots and beacons are accepted |
| The same message arrives twice | The duplicate is recognised and ignored, so the map never shows an event twice |
| Information is old | It is flagged as stale instead of being presented as current |
| A device restarts and counts from zero again | The ONA tells the new session apart from a replay |
| The real-world anchor for the Writer's map isn't trustworthy | Positions stay relative, and no false GPS is produced |
| The Writer is lost before it returns | The beacons it left still hold the key findings, so the information is not gone |

---

## 8. How This Meets the Challenge

The challenge requires a **functional Outside Network Area** and states that **all communication between inside and outside passes through it, with no direct link between the robots and the command post.** The ONA satisfies this by construction, and it covers the four roles the challenge names:

| Challenge expectation | How the ONA delivers it |
|---|---|
| Receive data from the Writer | Role 1 — Receive |
| Translate robot coordinates into real-world GPS | Role 2 — Translate |
| Transfer information to a distant command post | Role 3 — Carry |
| Brief the Executor before entry | Role 4 — Brief |
| Wireless / satellite link to the command post | Uplink used by the Carry role |
| Live map at the command post | Fed by the ONA's outgoing stream |

---

## 9. Where the Project Stands Today

The ONA's structure is defined and its foundations are in place. The deeper parts of the pipeline (message decoding, the full trust checks, coordinate translation, the retry queue and the long-range uplink) are still being built, and the **Brief** role is the next piece to add. The concept above describes the complete, intended behaviour of the system.

---

<p align="center"><i>Receive → Translate → Carry → Brief</i></p>
