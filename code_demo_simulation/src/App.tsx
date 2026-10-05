import { useEffect, useMemo, useState } from "react"
import gasFilteredImage from "./assets/gas-filtered.png"
import victimHelpedImage from "./assets/victim-helped.png"

type Screen = "writer" | "command" | "executor"
type Priority = "victim" | "gas"

const tabs: { id: Screen step: string label: string meta: string }[] = [
  {
    id: "writer",
    step: "01",
    label: "Writer Exploration",
    meta: "GPS-DENIED ZONE",
  },
  { id: "command", step: "02", label: "Command Post", meta: "OUTSIDE NETWORK" },
  {
    id: "executor",
    step: "03",
    label: "Executor Navigation",
    meta: "MISSION ACTIVE",
  },
]

const obstacles = [
  { x: 13, y: 12, w: 18, h: 7 },
  { x: 13, y: 19, w: 6, h: 20 },
  { x: 37, y: 9, w: 7, h: 21 },
  { x: 44, y: 24, w: 17, h: 6 },
  { x: 55, y: 30, w: 6, h: 18 },
  { x: 13, y: 52, w: 23, h: 6 },
  { x: 30, y: 58, w: 6, h: 17 },
  { x: 45, y: 43, w: 7, h: 19 },
  { x: 52, y: 56, w: 19, h: 6 },
  { x: 71, y: 14, w: 6, h: 19 },
  { x: 71, y: 33, w: 18, h: 6 },
  { x: 83, y: 45, w: 6, h: 20 },
  { x: 62, y: 69, w: 27, h: 7 },
  { x: 13, y: 76, w: 8, h: 12 },
  { x: 36, y: 75, w: 7, h: 13 },
]

const firstWriterPath = [
  [8, 88],
  [92, 88],
  [92, 78],
  [32, 78],
  [32, 74],
  [28, 74],
  [24, 74],
  [24, 78],
  [8, 78],
  [8, 68],
  [78, 68],
] as [number, number][]

const replacementWriterPath = [
  [8, 88],
  [22, 84],
  [38, 79],
  [54, 74],
  [68, 72],
  [78, 68],
  [72, 62],
  [78, 57],
  [85, 62],
  [78, 68],
  [92, 58],
  [8, 58],
  [8, 48],
  [52, 48],
  [62, 50],
  [61, 38],
  [76, 35],
  [82, 23],
  [76, 35],
  [67, 50],
  [92, 48],
  [92, 38],
  [8, 38],
  [8, 28],
  [92, 28],
  [92, 18],
  [8, 18],
] as [number, number][]

const normalWriterPath = [
  [8, 88],
  [92, 88],
  [92, 78],
  [32, 78],
  [32, 74],
  [28, 74],
  [24, 74],
  [24, 78],
  [8, 78],
  [8, 68],
  [92, 68],
  [92, 58],
  [8, 58],
  [8, 48],
  [52, 48],
  [62, 50],
  [61, 38],
  [76, 35],
  [82, 23],
  [76, 35],
  [67, 50],
  [92, 48],
  [92, 38],
  [8, 38],
  [8, 28],
  [92, 28],
  [92, 18],
  [8, 18],
] as [number, number][]

function pointOnPath(path: [number, number][], progress: number) {
  const exactIndex = Math.max(0, Math.min(1, progress)) * (path.length - 1)
  const pointIndex = Math.min(path.length - 1, Math.floor(exactIndex))
  const nextPoint = path[Math.min(path.length - 1, pointIndex + 1)]
  const segmentProgress = exactIndex - pointIndex
  const point: [number, number] = [
    path[pointIndex][0] +
      (nextPoint[0] - path[pointIndex][0]) * segmentProgress,
    path[pointIndex][1] +
      (nextPoint[1] - path[pointIndex][1]) * segmentProgress,
  ]

  return {
    point,
    visited: [...path.slice(0, pointIndex + 1), point] as [number, number][],
  }
}

function getWriterPosition(progress: number) {
  if (progress < 26) return pointOnPath(firstWriterPath, progress / 26).point
  return pointOnPath(replacementWriterPath, (progress - 30) / 70).point
}

function formatMissionTime(progress: number) {
  const seconds = Math.round(progress * 1.42)
  return `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(
    seconds % 60,
  ).padStart(2, "0")}`
}

type LocalPoint = [number, number]

const executorGasLocalRoute: LocalPoint[] = [
  [0, 0],
  [0, 5],
  [4, 5],
  [4, 10],
  [6, 10],
  [6, 12],
  [12, 12],
  [12, 9],
  [16, 9],
]

const executorVictimLocalRoute: LocalPoint[] = [
  ...executorGasLocalRoute,
  [16, 11],
  [23, 11],
  [23, 16],
  [20, 16],
]

function localPointToOccupancyMap([x, y]: LocalPoint): LocalPoint {
  return [8 + x * 3.7, 86 - y * 4]
}

const executorVictimRoute = executorVictimLocalRoute.map(
  localPointToOccupancyMap,
)
const executorGasRoute = executorGasLocalRoute.map(localPointToOccupancyMap)

const executorMedicalReturnRoute = [
  [82, 23],
  [94, 23],
  [94, 42],
  [67, 42],
  [67, 50],
  [50, 50],
  [50, 35],
  [30, 35],
  [30, 46],
  [24, 46],
  [24, 66],
  [8, 66],
  [8, 86],
] as [number, number][]

const executorGasReturnRoute = [
  [67, 50],
  [50, 50],
  [50, 35],
  [30, 35],
  [30, 46],
  [24, 46],
  [24, 66],
  [8, 66],
  [8, 86],
] as [number, number][]

function getMedicalRobotState(progress: number) {
  if (progress < 45) {
    const state = pointOnPath(executorVictimRoute, progress / 45)
    return { ...state, stage: "medical-route" }
  }
  if (progress < 58) {
    return {
      point: executorVictimRoute[executorVictimRoute.length - 1],
      visited: executorVictimRoute,
      stage: "medical-aid",
    }
  }
  const state = pointOnPath(executorMedicalReturnRoute, (progress - 58) / 42)
  return {
    point: state.point,
    visited: [...executorVictimRoute, ...state.visited],
    stage: progress >= 100 ? "complete" : "medical-return",
  }
}

function getGasRobotState(progress: number) {
  if (progress < 58) {
    const state = pointOnPath(executorGasRoute, progress / 58)
    return { ...state, stage: "gas-route" }
  }
  if (progress < 80) {
    return {
      point: executorGasRoute[executorGasRoute.length - 1],
      visited: executorGasRoute,
      stage: "gas-filter",
    }
  }
  const state = pointOnPath(executorGasReturnRoute, (progress - 80) / 20)
  return {
    point: state.point,
    visited: [...executorGasRoute, ...state.visited],
    stage: progress >= 100 ? "complete" : "gas-return",
  }
}

function Icon({ name, size = 18 }: { name: string size?: number }) {
  const paths: Record<string, React.ReactNode> = {
    pulse: <path d="M3 12h4l2-7 4 14 2-7h6" />,
    satellite: (
      <>
        <path d="m5 4 4 4-3 3-4-4 3-3Zm10 9 4 4-3 3-4-4 3-3Z" />
        <path d="m8 14 6-6M11 5a7 7 0 0 1 8 8M9 8a4 4 0 0 1 7 3" />
      </>
    ),
    robot: (
      <>
        <rect x="5" y="7" width="14" height="11" rx="2" />
        <path d="M9 7V4h6v3M9 12h.01M15 12h.01M8 18v2M16 18v2" />
      </>
    ),
    beacon: (
      <>
        <path d="M12 13v8M8 21h8M9 13h6l-1-6h-4l-1 6Z" />
        <path d="M7 4a7 7 0 0 0 0 9M17 4a7 7 0 0 1 0 9" />
      </>
    ),
    play: <path d="m8 5 11 7-11 7V5Z" />,
    pause: (
      <>
        <path d="M9 5v14M15 5v14" />
      </>
    ),
    refresh: (
      <path d="M20 7v5h-5M4 17v-5h5M6.1 8a7 7 0 0 1 11.5-2L20 8M4 16l2.4 2A7 7 0 0 0 18 16" />
    ),
    target: (
      <>
        <circle cx="12" cy="12" r="8" />
        <circle cx="12" cy="12" r="2" />
        <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
      </>
    ),
    chevron: <path d="m9 18 6-6-6-6" />,
    check: <path d="m5 12 4 4L19 6" />,
    shield: <path d="M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6l-7-3Z" />,
    compass: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="m15 7-2 6-4 4 2-6 4-4Z" />
      </>
    ),
  }
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  )
}

function Tag({
  children,
  tone = "cyan",
}: {
  children: React.ReactNode
  tone?: string
}) {
  return <span className={`tag tag-${tone}`}>{children}</span>
}

function SignalBars({ strength = 4 }: { strength?: number }) {
  return (
    <span className="signal-bars" aria-label={`${strength} of 4 signal bars`}>
      {[1, 2, 3, 4].map((bar) => (
        <i key={bar} className={bar <= strength ? "lit" : ""} />
      ))}
    </span>
  )
}

function PanelHeader({
  eyebrow,
  title,
  action,
}: {
  eyebrow: string
  title: string
  action?: React.ReactNode
}) {
  return (
    <div className="panel-header">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
      </div>
      {action}
    </div>
  )
}

function MapMarker({
  x,
  y,
  type,
  visible = true,
  compact = false,
}: {
  x: number
  y: number
  type: Priority
  visible?: boolean
  compact?: boolean
}) {
  if (!visible) return null
  return (
    <g className={`map-marker ${type}`}>
      <circle cx={x} cy={y} r={compact ? 5 : 6.5} className="marker-pulse" />
      <circle cx={x} cy={y} r={compact ? 2.6 : 3.2} className="marker-core" />
      {!compact && (
        <g transform={`translate(${x - 3.5} ${y + 5}) scale(.3)`}>
          <path d="M12 13v8M8 21h8M9 13h6l-1-6h-4l-1 6Z" />
          <path d="M7 4a7 7 0 0 0 0 9M17 4a7 7 0 0 1 0 9" />
        </g>
      )}
    </g>
  )
}

function RobotGlyph({
  x,
  y,
  executor = false,
  damaged = false,
  role,
}: {
  x: number
  y: number
  executor?: boolean
  damaged?: boolean
  role?: "medical" | "gas"
}) {
  return (
    <g
      transform={`translate(${x - 5} ${y - 5})`}
      className={`robot-glyph ${executor ? "executor" : ""} ${
        damaged ? "damaged" : ""
      } ${role ? `role-${role}` : ""}`}
    >
      <circle cx="5" cy="5" r="7.5" className="robot-aura" />
      <rect x="1" y="1" width="8" height="8" rx="2" className="robot-body" />
      <path d="M3 1V0h4v1M3.2 4.5h.1M6.7 4.5h.1M2 9v1M8 9v1" />
      {damaged && <path className="damage-x" d="m2 2 6 6m0-6L2 8" />}
    </g>
  )
}

function IncidentRouteTrace({
  route,
  tone,
}: {
  route: LocalPoint[]
  tone: Priority
}) {
  const maxX = Math.max(...route.map(([x]) => x))
  const maxY = Math.max(...route.map(([, y]) => y))
  const points = route
    .map(([x, y]) => `${5 + (x / maxX) * 90},${45 - (y / maxY) * 40}`)
    .join(" ")
  const destination = points.split(" ").at(-1)?.split(",") ?? ["95", "5"]

  return (
    <div className={`incident-route incident-route-${tone}`}>
      <div className="incident-route-head">
        <span>EXECUTOR PATH TRACE</span>
        <b>{route.length - 1} LEGS</b>
      </div>
      <svg viewBox="0 0 100 50" role="img" aria-label={`${tone} executor path`}>
        <polyline points={points} />
        <circle cx="5" cy="45" r="2.2" className="route-origin" />
        <circle
          cx={destination[0]}
          cy={destination[1]}
          r="2.5"
          className="route-destination"
        />
      </svg>
      <code>{route.map(([x, y]) => `(${x},${y})`).join(" → ")}</code>
    </div>
  )
}

function OccupancyMap({
  mode,
  progress,
  failureCase = true,
}: {
  mode: "writer" | "executor"
  progress: number
  failureCase?: boolean
}) {
  const medicalMission = getMedicalRobotState(progress)
  const gasMission = getGasRobotState(progress)
  const firstWriterState = pointOnPath(
    firstWriterPath,
    Math.min(1, progress / 26),
  )
  const replacementWriterState = pointOnPath(
    replacementWriterPath,
    Math.max(0, (progress - 30) / 70),
  )
  const normalWriterState = pointOnPath(normalWriterPath, progress / 100)
  const visitedPath =
    mode === "writer"
      ? failureCase
        ? replacementWriterState.visited
        : normalWriterState.visited
      : medicalMission.visited
  const pathString = visitedPath.map((p) => p.join(",")).join(" ")
  const gasPathString = gasMission.visited.map((p) => p.join(",")).join(" ")
  const firstPathString = firstWriterState.visited
    .map((p) => p.join(","))
    .join(" ")
  const activeWriter =
    failureCase && progress < 26
      ? firstWriterState.point
      : failureCase
        ? replacementWriterState.point
        : normalWriterState.point
  const victimThreshold = failureCase ? 78 : 60
  const gasThreshold = failureCase ? 88 : 69
  const helpThreshold = failureCase ? 69 : 50
  const reachedVictim = mode === "executor" || progress >= victimThreshold
  const reachedGas = mode === "executor" || progress >= gasThreshold
  const victimResolved = mode === "executor" && progress >= 58
  const gasResolved = mode === "executor" && progress >= 80
  const helpHeard =
    mode === "writer" && progress >= helpThreshold && progress < victimThreshold

  return (
    <div className="occupancy-wrap">
      <svg
        className="occupancy-map"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        role="img"
        aria-label="Robot occupancy map"
      >
        <defs>
          <pattern
            id={`grid-${mode}`}
            width="4"
            height="4"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 4 0 L 0 0 0 4"
              fill="none"
              stroke="#66717d"
              strokeWidth=".22"
            />
          </pattern>
          <clipPath id={`reveal-${mode}`}>
            {mode === "writer" ? (
              <>
                {[
                  ...(failureCase ? firstWriterState.visited : []),
                  ...visitedPath,
                ].map((point, index) => (
                  <circle key={index} cx={point[0]} cy={point[1]} r="13" />
                ))}
              </>
            ) : (
              <rect width="100" height="100" />
            )}
          </clipPath>
          <radialGradient id="hazard" cx="50%" cy="50%">
            <stop offset="0%" stopColor="#ffb340" stopOpacity=".46" />
            <stop offset="70%" stopColor="#ffb340" stopOpacity=".17" />
            <stop offset="100%" stopColor="#ffb340" stopOpacity="0" />
          </radialGradient>
        </defs>
        <rect width="100" height="100" fill="#353d46" />
        <rect width="100" height="100" fill={`url(#grid-${mode})`} />
        <g clipPath={`url(#reveal-${mode})`}>
          <rect x="4" y="5" width="92" height="90" rx="1" fill="#d5d9da" />
          <rect
            x="4"
            y="5"
            width="92"
            height="90"
            fill={`url(#grid-${mode})`}
            opacity=".46"
          />
          {obstacles.map((o, index) => (
            <rect key={index} {...o} fill="#11171c" />
          ))}
          {mode === "writer" && (
            <g className="avoidance-cube">
              <rect x="26" y="76" width="4" height="4" />
              <path d="m26 76 2-2 4 0-2 2m2-2v4l-2 2" />
              <text x="31.5" y="81.5">
                CUBE (5,5)
              </text>
            </g>
          )}
        </g>
        {mode === "executor" && !gasResolved && (
          <circle
            cx="67"
            cy="50"
            r="18"
            fill="url(#hazard)"
            className="hazard-breathe"
          />
        )}
        {mode === "executor" && !gasResolved && (
          <circle
            cx="67"
            cy="50"
            r="11"
            fill="none"
            stroke="#ffb340"
            strokeWidth=".7"
            strokeDasharray="2 1.4"
          />
        )}
        {mode === "writer" && reachedGas && (
          <g className="gas-contours">
            <circle cx="67" cy="50" r="16" />
            <circle cx="67" cy="50" r="10" />
            <circle cx="67" cy="50" r="5" />
          </g>
        )}
        {mode === "writer" && reachedVictim && (
          <g className="broken-wall">
            <path d="M76 18h7l-2 3 3 2-3 3h8" />
            <text x="76" y="16">
              BREACH
            </text>
          </g>
        )}
        {mode === "writer" && failureCase && progress >= 26 && (
          <g
            className={`trap-zone ${
              progress >= 30 && progress < 49 ? "scanning" : ""
            }`}
          >
            <circle cx="78" cy="68" r="10" />
            <path d="m70 61 4 3 3-5 4 4 6-3M70 75l5-3 4 4 4-5 5 2" />
            <text x="68" y="57">
              COLLAPSE TRAP
            </text>
          </g>
        )}
        {mode === "writer" && failureCase && (
          <polyline
            points={firstPathString}
            fill="none"
            stroke="#ff5b52"
            strokeWidth="1.1"
            strokeDasharray="1.8 1.5"
            opacity=".72"
          />
        )}
        {mode === "writer" ? (
          <polyline
            points={pathString}
            fill="none"
            stroke="#00d8ff"
            strokeWidth="1.1"
            strokeDasharray="1.8 1.5"
            opacity=".88"
          />
        ) : (
          <>
            <polyline
              points={pathString}
              fill="none"
              stroke="#ff5b52"
              strokeWidth="1.1"
              opacity=".88"
            />
            <polyline
              points={gasPathString}
              fill="none"
              stroke="#ffb340"
              strokeWidth="1.1"
              opacity=".88"
            />
          </>
        )}
        <MapMarker
          x={82}
          y={23}
          type="victim"
          visible={mode === "executor" ? !victimResolved : reachedVictim}
        />
        <MapMarker
          x={67}
          y={50}
          type="gas"
          visible={mode === "executor" ? !gasResolved : reachedGas}
        />
        {helpHeard && (
          <g className="audio-bearing">
            <path d="M70 30q8-8 16 0M73 33q5-5 10 0" />
            <text x="70" y="27">
              “HELP”
            </text>
          </g>
        )}
        {mode === "executor" && (
          <g className="origin-marker">
            <circle cx="8" cy="86" r="3.5" />
            <path d="M4 86h8M8 82v8" />
            <text x="3" y="94">
              ORIGIN 0,0
            </text>
          </g>
        )}
        {mode === "writer" && failureCase && progress >= 26 && (
          <>
            <RobotGlyph x={78} y={68} damaged />
            <text x="72" y="76" className="svg-label red-label">
              WR-07 / IMMOBILE
            </text>
          </>
        )}
        {mode === "writer" ? (
          <RobotGlyph x={activeWriter[0]} y={activeWriter[1]} />
        ) : (
          <>
            <RobotGlyph
              x={medicalMission.point[0]}
              y={medicalMission.point[1]}
              executor
              role="medical"
            />
            <text
              x={medicalMission.point[0] + 3}
              y={medicalMission.point[1] - 5}
              className="svg-label red-label"
            >
              MED-04
            </text>
            <RobotGlyph
              x={gasMission.point[0]}
              y={gasMission.point[1]}
              executor
              role="gas"
            />
            <text
              x={gasMission.point[0] + 3}
              y={gasMission.point[1] + 7}
              className="svg-label amber-label"
            >
              GAS-09
            </text>
          </>
        )}
        {mode === "writer" && failureCase && progress >= 26 && (
          <text
            x={activeWriter[0] + 3}
            y={activeWriter[1] - 5}
            className="svg-label"
          >
            WR-08
          </text>
        )}
        <text x="6" y="4" className="svg-label">
          N ↑
        </text>
        {reachedVictim && !victimResolved && (
          <text x="79" y="17" className="svg-label red-label">
            V-01 / BCN
          </text>
        )}
        {reachedGas && !gasResolved && (
          <text x="63" y="43" className="svg-label amber-label">
            G-02 / BCN
          </text>
        )}
      </svg>
      <div className="map-coordinates">LOCAL FRAME / ORIGIN 0,0</div>
      <div className="map-legend">
        <span>
          <i className="free" /> FREE
        </span>
        <span>
          <i className="occupied" /> OBSTACLE
        </span>
        <span>
          <i className="unknown" /> UNKNOWN
        </span>
      </div>
      {mode === "writer" && (
        <div
          className={`search-mode ${
            helpHeard || (failureCase && progress >= 26 && progress < 30)
              ? "priority"
              : ""
          }`}
        >
          <span />
          {failureCase && progress < 26 && "WR-07 / boustrophedon sweep"}
          {failureCase &&
            progress >= 26 &&
            progress < 30 &&
            "WR-07 damaged / replacement dispatched"}
          {failureCase &&
            progress >= 30 &&
            progress < 39 &&
            "WR-08 / direct insertion — snake scan bypassed"}
          {failureCase &&
            progress >= 39 &&
            progress < 49 &&
            "Local perimeter scan / trap identified"}
          {failureCase &&
            progress >= 49 &&
            progress < 69 &&
            "Chemical anomaly / climbing gradient"}
          {failureCase &&
            helpHeard &&
            "Priority override / acoustic HELP bearing"}
          {failureCase &&
            progress >= 78 &&
            progress < 88 &&
            "V-01 payload written / resuming gas trace"}
          {failureCase &&
            progress >= 88 &&
            "G-02 payload written / sweep resumed"}
          {!failureCase &&
            progress < 41 &&
            "Boustrophedon sweep / wall-to-wall"}
          {!failureCase &&
            progress >= 41 &&
            progress < 50 &&
            "Chemical anomaly / climbing gradient"}
          {!failureCase &&
            helpHeard &&
            "Priority override / acoustic HELP bearing"}
          {!failureCase &&
            progress >= 60 &&
            progress < 69 &&
            "V-01 payload written / resuming gas trace"}
          {!failureCase &&
            progress >= 69 &&
            "G-02 payload written / sweep resumed"}
        </div>
      )}
      {mode === "executor" && (
        <div className={`hazard-label ${gasResolved ? "resolved" : ""}`}>
          <span />{" "}
          {gasResolved
            ? "BOTH ROBOTS RETURNING · OBJECTIVES SAFE"
            : progress >= 58
              ? "MED-04 COMPLETE · GAS-09 FILTERING"
              : progress >= 45
                ? "MED-04 AID ACTIVE · GAS-09 APPROACHING"
                : "2 EXECUTORS DEPLOYED · GLOBAL GPS LOCK"}
        </div>
      )}
    </div>
  )
}

function Metric({
  label,
  value,
  unit,
}: {
  label: string
  value: string
  unit?: string
}) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
      {unit && <small>{unit}</small>}
    </div>
  )
}

function WriterView({ onContinue }: { onContinue: () => void }) {
  const [progress, setProgress] = useState(4)
  const [playing, setPlaying] = useState(true)
  const [failureCase, setFailureCase] = useState(true)

  useEffect(() => {
    if (!playing || progress >= 100) return
    const timer = window.setInterval(
      () => setProgress((p) => Math.min(100, p + 1)),
      260,
    )
    return () => window.clearInterval(timer)
  }, [playing, progress])

  useEffect(() => {
    if (progress >= 100) setPlaying(false)
  }, [progress])

  const anomalyThreshold = failureCase ? 49 : 41
  const helpThreshold = failureCase ? 69 : 50
  const victimThreshold = failureCase ? 78 : 60
  const gasThreshold = failureCase ? 88 : 69
  const gas = failureCase
    ? progress < 49
      ? 14 + Math.round(progress / 8)
      : progress < 69
        ? 22 + Math.round((progress - 49) * 5)
        : progress < 78
          ? 122 - Math.round((progress - 69) * 6)
          : progress < 88
            ? 68 + Math.round((progress - 78) * 36)
            : 428
    : progress < 41
      ? 14 + Math.round(progress / 8)
      : progress < 50
        ? 22 + Math.round((progress - 41) * 9)
        : progress < 60
          ? 103 - Math.round((progress - 50) * 5)
          : progress < 69
            ? 54 + Math.round((progress - 60) * 42)
            : 428
  const helpDb = failureCase
    ? progress < 64
      ? 24 + Math.round(progress / 16)
      : progress < 78
        ? 28 + Math.round((progress - 64) * 3.8)
        : 81
    : progress < 46
      ? 24 + Math.round(progress / 16)
      : progress < 60
        ? 28 + Math.round((progress - 46) * 3.8)
        : 81
  const writerPosition = failureCase
    ? getWriterPosition(progress)
    : pointOnPath(normalWriterPath, progress / 100).point
  const writerId = failureCase ? "WR-08" : "WR-07"
  const victimWriteTime = formatMissionTime(victimThreshold)
  const gasWriteTime = formatMissionTime(gasThreshold)
  const confidence =
    progress >= gasThreshold
      ? 98
      : progress >= victimThreshold
        ? 96
        : progress >= helpThreshold
          ? 91
          : progress >= anomalyThreshold
            ? 64
            : 28 + Math.floor(progress / 4)
  const scanMode = failureCase
    ? progress < 26
      ? "SNAKE SCAN"
      : progress < 30
        ? "WRITER FAILURE"
        : progress < 39
          ? "DIRECT INSERT"
          : progress < 49
            ? "TRAP SURVEY"
            : progress < 69
              ? "GAS GRADIENT"
              : progress < 78
                ? "HELP OVERRIDE"
                : progress < 88
                  ? "RESUME GAS"
                  : "AREA SWEEP"
    : progress < 41
      ? "SNAKE SCAN"
      : progress < 50
        ? "GAS GRADIENT"
        : progress < 60
          ? "HELP OVERRIDE"
          : progress < 69
            ? "RESUME GAS"
            : "AREA SWEEP"

  return (
    <section className="screen-view">
      <div className="view-intro">
        <div>
          <div className="step-line">
            <span>PHASE 01</span>
            <i />
            AUTONOMOUS EXPLORATION
          </div>
          <h1>
            Writer Robot{" "}
            <em>/ {failureCase && progress >= 26 ? "WR-08" : "WR-07"}</em>
          </h1>
          <p>
            {failureCase
              ? "WR-07 sweep, failure recovery, and hazard-aware WR-08 continuation."
              : "WR-07 uninterrupted wall-to-wall exploration and sensor-priority search."}
          </p>
        </div>
        <div className="live-pill">
          <span /> LIVE TELEMETRY <b>18 Hz</b>
        </div>
      </div>

      <div className="writer-layout">
        <div className="map-panel panel">
          <PanelHeader
            eyebrow="SLAM / OCCUPANCY GRID"
            title="Exploration Matrix"
            action={<Tag>{Math.round(progress * 0.92)}% MAPPED</Tag>}
          />
          <OccupancyMap
            mode="writer"
            progress={progress}
            failureCase={failureCase}
          />
          <div className="map-controls">
            <button
              className={`case-toggle ${failureCase ? "active" : ""}`}
              aria-pressed={failureCase}
              onClick={() => {
                setFailureCase((enabled) => !enabled)
                setProgress(4)
                setPlaying(true)
              }}
            >
              FAILURE CASE · {failureCase ? "ON" : "OFF"}
            </button>
            <button
              className="icon-button"
              onClick={() => setPlaying(!playing)}
              aria-label={playing ? "Pause exploration" : "Play exploration"}
            >
              <Icon name={playing ? "pause" : "play"} size={16} />
            </button>
            <button
              className="icon-button"
              onClick={() => {
                setProgress(4)
                setPlaying(true)
              }}
              aria-label="Reset exploration"
            >
              <Icon name="refresh" size={16} />
            </button>
            <div className="timeline">
              <span>MISSION ELAPSED</span>
              <div>
                <i style={{ width: `${progress}%` }} />
              </div>
              <b>00:{String(Math.round(progress * 1.42)).padStart(2, "0")}</b>
            </div>
            <button className="primary-action compact" onClick={onContinue}>
              COMMAND POST <Icon name="chevron" size={15} />
            </button>
          </div>
        </div>

        <aside className="writer-sidebar">
          <div className="panel telemetry-panel">
            <PanelHeader
              eyebrow="SENSOR ARRAY"
              title={scanMode}
              action={
                <span className="sample-rate">
                  {progress >= helpThreshold && progress < victimThreshold
                    ? "AUDIO LOCK"
                    : "Δ 55ms"}
                </span>
              }
            />
            <div className="metrics-grid">
              <Metric
                label="WRITER POSITION (X,Y)"
                value={`${writerPosition[0].toFixed(1)}, ${writerPosition[1].toFixed(1)}`}
                unit="m"
              />
              <Metric
                label="GYRO HEADING"
                value={`${Math.round((progress * 11.7) % 360)}°`}
                unit={Math.floor(progress / 5) % 2 ? "W" : "E"}
              />
              <Metric label="GAS SENSOR" value={`${gas}`} unit="ppm" />
              <Metric label="HELP HEARING" value={`${helpDb}`} unit="dB" />
            </div>
            <div className="confidence">
              <div>
                <span>DETECTION CONFIDENCE</span>
                <b>{confidence}%</b>
              </div>
              <div className="bar">
                <i style={{ width: `${confidence}%` }} />
              </div>
              <small>
                {progress >= helpThreshold && progress < victimThreshold
                  ? "AUDIO CLASSIFIER / KEYWORD: “HELP”"
                  : failureCase && progress >= 26 && progress < 49
                    ? "FUSED / LIDAR + DAMAGE MEMORY + PROXIMITY"
                    : "FUSED / LIDAR + CAMERA + MQ-2"}
              </small>
            </div>
            <div className="sparkline" aria-hidden="true">
              <svg viewBox="0 0 300 54" preserveAspectRatio="none">
                <path
                  d={
                    progress < anomalyThreshold
                      ? "M0 40 L30 39 60 41 90 38 120 40 150 39 180 40 210 38 240 39 270 37 300 38"
                      : progress < victimThreshold
                        ? "M0 43 L35 41 70 38 105 34 140 27 175 18 210 22 245 30 275 33 300 36"
                        : "M0 44 L30 40 65 36 100 30 135 24 170 17 205 13 240 9 270 6 300 4"
                  }
                />
                <line x1="0" y1="40" x2="300" y2="40" />
              </svg>
            </div>
          </div>

          <div className="panel event-log">
            <PanelHeader
              eyebrow="EVENT BUFFER"
              title="Beacon Depositions"
              action={
                <Tag
                  tone={
                    progress >= gasThreshold
                      ? "red"
                      : (failureCase && progress >= 26) ||
                          progress >= victimThreshold
                        ? "amber"
                        : "muted"
                  }
                >
                  {progress >= gasThreshold
                    ? failureCase
                      ? "03 EVENTS"
                      : "02 EVENTS"
                    : progress >= victimThreshold
                      ? failureCase
                        ? "02 EVENTS"
                        : "01 EVENT"
                      : failureCase && progress >= 26
                        ? "01 EVENT"
                        : "SCANNING"}
                </Tag>
              }
            />
            {failureCase && (
              <div
                className={`event-row failure ${
                  progress >= 26 ? "detected" : ""
                } ${progress >= 30 && progress < 49 ? "tracking" : ""}`}
              >
                <div className="event-icon">
                  <Icon name={progress >= 26 ? "robot" : "pulse"} size={17} />
                </div>
                <div>
                  <b>
                    {progress >= 49
                      ? "TRAP MAPPED / WR-08 CLEAR"
                      : progress >= 30
                        ? "WR-08 PERIMETER SURVEY"
                        : progress >= 26
                          ? "WR-07 IMMOBILIZED"
                          : "WRITER STATUS NOMINAL"}
                  </b>
                  <span>
                    {progress >= 49
                      ? "Collapse hazard remembered · exploration resumed"
                      : progress >= 30
                        ? "Direct insertion · checking WR-07 surroundings"
                        : progress >= 26
                          ? "Motion lost before victim or gas discovery"
                          : "Primary writer executing snake sweep"}
                  </span>
                </div>
                <strong>
                  {progress >= 49
                    ? "AVOID"
                    : progress >= 26
                      ? "FAILED"
                      : "ACTIVE"}
                </strong>
              </div>
            )}
            <div
              className={`event-row amber ${
                progress >= gasThreshold ? "detected" : ""
              } ${
                progress >= anomalyThreshold && progress < helpThreshold
                  ? "tracking"
                  : ""
              }`}
            >
              <div className="event-icon">
                <Icon
                  name={progress >= gasThreshold ? "beacon" : "pulse"}
                  size={17}
                />
              </div>
              <div>
                <b>
                  {progress >= gasThreshold
                    ? "BCN G-02 · GAS_LEAK 428PPM"
                    : progress >= anomalyThreshold
                      ? "CHEMICAL ANOMALY"
                      : "NO CHEMICAL EVENT"}
                </b>
                <span>
                  {progress >= gasThreshold
                    ? `GO E→PEAK · ${writerId}@${gasWriteTime} · BCN(67,50)`
                    : progress >= anomalyThreshold
                      ? "Gradient rising · source unknown"
                      : "Background concentration nominal"}
                </span>
              </div>
              <strong>
                {progress >= gasThreshold
                  ? "DROPPED"
                  : progress >= anomalyThreshold
                    ? `${gas} PPM`
                    : "SEARCHING"}
              </strong>
            </div>
            <div
              className={`event-row red ${
                progress >= victimThreshold ? "detected" : ""
              } ${
                progress >= helpThreshold && progress < victimThreshold
                  ? "tracking"
                  : ""
              }`}
            >
              <div className="event-icon">
                <Icon
                  name={progress >= victimThreshold ? "beacon" : "pulse"}
                  size={17}
                />
              </div>
              <div>
                <b>
                  {progress >= victimThreshold
                    ? "BCN V-01 · VICTIM_TRAPPED"
                    : progress >= helpThreshold
                      ? "VOICE DETECTED: “HELP”"
                      : "NO ACOUSTIC EVENT"}
                </b>
                <span>
                  {progress >= victimThreshold
                    ? `GO NE→BREACH · ${writerId}@${victimWriteTime} · BCN(82,23)`
                    : progress >= helpThreshold
                      ? `Bearing triangulation · ${helpDb} dB and rising`
                      : "Listening during autonomous sweep"}
                </span>
              </div>
              <strong>
                {progress >= victimThreshold
                  ? "96% CONF."
                  : progress >= helpThreshold
                    ? `${helpDb} DB`
                    : "SEARCHING"}
              </strong>
            </div>
            <p className="buffer-note">
              <Icon name="shield" size={14} />{" "}
              {failureCase
                ? "Replacement writers inherit damage memory, inspect the failure perimeter, then resume safely."
                : "Standard writer exploration continues unless sensor priority interrupts the sweep."}
            </p>
          </div>
        </aside>
      </div>
    </section>
  )
}

const links = [
  ["Writer ↔ Beacon", 4, "868 MHz"],
  ["Beacon ↔ Beacon", 3, "MESH"],
  ["Writer ↔ ONA", 2, "LORA"],
  ["ONA ↔ Command Post", 4, "SAT"],
  ["ONA ↔ Executor", 3, "2.4 GHz"],
] as const

function CommandView({ onDeploy }: { onDeploy: () => void }) {
  return (
    <section className="screen-view">
      <div className="view-intro">
        <div>
          <div className="step-line">
            <span>PHASE 02</span>
            <i />
            FRAME TRANSLATION + MISSION CONTROL
          </div>
          <h1>
            Command Post <em>/ CP-NORTH</em>
          </h1>
          <p>Local coordinates translated through the Outside Network Area.</p>
        </div>
        <div className="live-pill">
          <span /> ONA UPLINK <b>STABLE</b>
        </div>
      </div>

      <div className="command-layout">
        <div className="panel geo-panel">
          <PanelHeader
            eyebrow="GEOSPATIAL OVERLAY / 36.8065° N, 10.1815° E"
            title="Live Incident Map"
            action={<Tag>GPS LOCK · ±1.8M</Tag>}
          />
          <div className="geo-map">
            <div className="terrain t1" />
            <div className="terrain t2" />
            <div className="terrain t3" />
            <svg viewBox="0 0 1000 580" preserveAspectRatio="none">
              <g className="blocks">
                <path d="M0 96 184 66l47 87-139 56L0 189ZM302 0l155 0 21 100-133 35ZM569 22l146-16 76 91-168 55ZM802 165l198-29v140l-153 21ZM40 324l196-57 82 114-206 70ZM392 247l173-74 87 125-195 67ZM686 361l172-46 142 96v169H817Z" />
              </g>
              <g className="roads">
                <path d="M-10 478C160 416 203 327 340 294S614 262 1010 82" />
                <path d="M106 590c45-122 110-225 196-312S443 118 496-10" />
                <path d="M461 590c2-86 48-161 146-242s155-172 174-358" />
                <path d="M-10 211c192-31 348-12 459 56s298 69 561 16" />
              </g>
              <g className="road-centers">
                <path d="M-10 478C160 416 203 327 340 294S614 262 1010 82" />
                <path d="M106 590c45-122 110-225 196-312S443 118 496-10" />
                <path d="M461 590c2-86 48-161 146-242s155-172 174-358" />
              </g>
            </svg>
            <div className="map-crosshair">
              <i />
              <i />
            </div>
            <div className="geo-north">
              N<br />
              <span>↑</span>
            </div>
            <div className="geo-scale">
              0 <i /> 25 <i /> 50 m
            </div>

            <div className="pin pin-victim">
              <span className="pin-head">
                <Icon name="target" size={17} />
              </span>
              <div className="popup-card">
                <div>
                  <Tag tone="red">PRIORITY 1</Tag>
                  <small>10:42:18 UTC</small>
                </div>
                <h3>VICTIM_TRAPPED</h3>
                <p>Thermal signature detected below structural debris.</p>
                <IncidentRouteTrace
                  route={executorVictimLocalRoute}
                  tone="victim"
                />
                <div className="popup-stats">
                  <span>
                    STATUS <b>RESPONSIVE</b>
                  </span>
                  <span>
                    CONFIDENCE <b>96%</b>
                  </span>
                </div>
              </div>
            </div>

            <div className="pin pin-gas">
              <span className="pin-head">
                <Icon name="target" size={17} />
              </span>
              <div className="popup-card">
                <div>
                  <Tag tone="amber">HAZARD</Tag>
                  <small>10:40:32 UTC</small>
                </div>
                <h3>GAS_LEAK</h3>
                <p>Combustible gas plume in eastern service corridor.</p>
                <IncidentRouteTrace route={executorGasLocalRoute} tone="gas" />
                <div className="popup-stats">
                  <span>
                    READING <b>428 PPM</b>
                  </span>
                  <span>
                    RADIUS <b>4.8 M</b>
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div className="translation-strip">
            <span>
              LOCAL FRAME <b>x 8.2 / y 2.3</b>
            </span>
            <Icon name="chevron" size={17} />
            <span>
              ONA TRANSFORM <b>EPSG:4326</b>
            </span>
            <Icon name="chevron" size={17} />
            <span>
              GLOBAL FRAME <b>36.8067 / 10.1821</b>
            </span>
          </div>
        </div>

        <aside className="command-sidebar">
          <div className="panel fleet-panel">
            <PanelHeader
              eyebrow="FLEET ORCHESTRATION"
              title="Executor Dashboard"
              action={<Tag>2 / 4 SELECTED</Tag>}
            />
            <div className="fleet-card standby">
              <Icon name="robot" size={17} />
              <span>
                <b>FIRE-03 · Firefighting robot</b>
                <small>BASE GPS 36.8067, 10.1821</small>
              </span>
              <Tag tone="muted">STANDBY</Tag>
            </div>
            <div className="fleet-card assigned medical">
              <Icon name="robot" size={17} />
              <span>
                <b>MED-04 · Medical robot</b>
                <small>V-01 GPS 36.8072, 10.1830</small>
              </span>
              <Tag tone="red">SELECTED</Tag>
            </div>
            <div className="fleet-card assigned gas">
              <Icon name="robot" size={17} />
              <span>
                <b>GAS-09 · Gas-filter robot</b>
                <small>G-02 GPS 36.8064, 10.1816</small>
              </span>
              <Tag tone="amber">SELECTED</Tag>
            </div>
            <div className="fleet-card standby">
              <Icon name="robot" size={17} />
              <span>
                <b>CLEAR-06 · Path-clearing robot</b>
                <small>BASE GPS 36.8067, 10.1821</small>
              </span>
              <Tag tone="muted">STANDBY</Tag>
            </div>
            <button className="primary-action deploy" onClick={onDeploy}>
              SEND 2 ROBOTS + GLOBAL GPS <Icon name="chevron" size={16} />
            </button>
          </div>

          <div className="panel links-panel">
            <PanelHeader
              eyebrow="RESILIENT COMMS"
              title="Link Health"
              action={<Tag>5 / 5 ONLINE</Tag>}
            />
            <div className="architecture-note">
              <Icon name="satellite" size={18} />
              <span>
                All external traffic routed through <b>ONA-01</b>
              </span>
            </div>
            {links.map(([name, strength, protocol]) => (
              <div className="link-row" key={name}>
                <span className="status-dot" />
                <div>
                  <b>{name}</b>
                  <small>{protocol}</small>
                </div>
                <SignalBars strength={strength} />
                <strong>{-34 - (4 - strength) * 13} dBm</strong>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </section>
  )
}

function ExecutorView({ onCommand }: { onCommand: () => void }) {
  const [progress, setProgress] = useState(0)
  const [running, setRunning] = useState(false)

  useEffect(() => {
    if (!running || progress >= 100) return
    const timer = window.setInterval(
      () => setProgress((p) => Math.min(100, p + 1)),
      280,
    )
    return () => window.clearInterval(timer)
  }, [running, progress])

  useEffect(() => {
    if (progress >= 100) setRunning(false)
  }, [progress])

  const complete = progress === 100
  const medicalProgress =
    progress < 45
      ? progress / 45
      : progress < 58
        ? (progress - 45) / 13
        : (progress - 58) / 42
  const gasProgress =
    progress < 58
      ? progress / 58
      : progress < 80
        ? (progress - 58) / 22
        : (progress - 80) / 20
  const medicalDistance =
    progress < 45
      ? 64 * (1 - medicalProgress)
      : progress < 58
        ? 0
        : 64 * (1 - medicalProgress)
  const gasDistance =
    progress < 58
      ? 41 * (1 - gasProgress)
      : progress < 80
        ? 0
        : 41 * (1 - gasProgress)
  const stageTitle =
    progress < 45
      ? "Two Robots En Route"
      : progress < 58
        ? "Medical Aid In Progress"
        : progress < 80
          ? "Gas Filtration In Progress"
          : progress < 100
            ? "Both Robots Returning"
            : "Mission Complete"

  return (
    <section className="screen-view">
      <div className="view-intro">
        <div>
          <div className="step-line">
            <span>PHASE 03</span>
            <i />
            INHERITED SPATIAL MEMORY
          </div>
          <h1>
            Executor Fleet <em>/ MED-04 + GAS-09</em>
          </h1>
          <p>
            Two specialized robots navigating from global GPS mission
            assignments.
          </p>
        </div>
        <div className={`live-pill ${complete ? "complete" : ""}`}>
          <span />{" "}
          {complete
            ? "MISSION COMPLETE"
            : running
              ? (progress >= 45 && progress < 58) ||
                (progress >= 58 && progress < 80)
                ? "INTERVENTION ACTIVE"
                : "NAVIGATION ACTIVE"
              : "AWAITING DEPLOY"}{" "}
          <b>{complete ? "SYNCED" : "AUTO"}</b>
        </div>
      </div>

      <div className="executor-layout">
        <div className="panel executor-map-panel">
          <PanelHeader
            eyebrow="LOCALIZATION / INHERITED MAP"
            title="Executor Route"
            action={
              <Tag tone={complete ? "cyan" : "amber"}>
                02 ROBOTS · {stageTitle.toUpperCase()}
              </Tag>
            }
          />
          <OccupancyMap mode="executor" progress={progress} />
          <div className="route-footer">
            <div>
              <span>ROUTE MODE</span>
              <b>DUAL EXECUTOR / GLOBAL GPS</b>
            </div>
            <div>
              <span>MED-04 · {progress >= 58 ? "TO ORIGIN" : "TO VICTIM"}</span>
              <b>{medicalDistance.toFixed(1)} M</b>
            </div>
            <div>
              <span>GAS-09 · {progress >= 80 ? "TO ORIGIN" : "TO LEAK"}</span>
              <b>{gasDistance.toFixed(1)} M</b>
            </div>
            <button
              className="primary-action compact"
              disabled={complete}
              onClick={() => setRunning(!running)}
            >
              <Icon name={running ? "pause" : "play"} size={15} />{" "}
              {complete
                ? "COMPLETE"
                : running
                  ? "PAUSE"
                  : progress
                    ? "RESUME"
                    : "START MISSION"}
            </button>
          </div>
        </div>

        <aside className="executor-sidebar">
          <div className="panel executor-fleet-panel">
            <PanelHeader
              eyebrow="ACTIVE FLEET"
              title="Two Executors"
              action={<Tag>GLOBAL GPS LOCK</Tag>}
            />
            <div className="executor-unit medical">
              <div className="executor-unit-head">
                <Icon name="robot" size={19} />
                <span>
                  <b>MED-04 · MEDICAL ROBOT</b>
                  <small>GPS 36.8072, 10.1830 · V-01</small>
                </span>
                <Tag tone="red">
                  {progress < 45
                    ? "EN ROUTE"
                    : progress < 58
                      ? "AID ACTIVE"
                      : progress < 100
                        ? "RETURNING"
                        : "HOME"}
                </Tag>
              </div>
              <div className="bar">
                <i style={{ width: `${progress}%` }} />
              </div>
              <p>
                {progress < 45
                  ? "Navigating to victim"
                  : progress < 58
                    ? "Dropping medical help bag"
                    : "Victim helped · returning to origin"}
              </p>
            </div>
            <div className="executor-unit gas">
              <div className="executor-unit-head">
                <Icon name="robot" size={19} />
                <span>
                  <b>GAS-09 · GAS-FILTER ROBOT</b>
                  <small>GPS 36.8064, 10.1816 · G-02</small>
                </span>
                <Tag tone="amber">
                  {progress < 58
                    ? "EN ROUTE"
                    : progress < 80
                      ? "FILTERING"
                      : progress < 100
                        ? "RETURNING"
                        : "HOME"}
                </Tag>
              </div>
              <div className="bar">
                <i style={{ width: `${progress}%` }} />
              </div>
              <p>
                {progress < 58
                  ? "Navigating to gas leak"
                  : progress < 80
                    ? "Filtering gas and sealing leak"
                    : "Leak stopped · returning to origin"}
              </p>
            </div>
          </div>

          {!complete ? (
            <div className="panel mission-brief">
              <PanelHeader eyebrow="ACTIVE OBJECTIVE" title={stageTitle} />
              {progress >= 45 && (
                <div className="mission-evidence">
                  <img
                    src={progress < 58 ? victimHelpedImage : gasFilteredImage}
                    alt={
                      progress < 58
                        ? "Executor robot helping the victim with a medical aid bag"
                        : "Gas leak transformed from polluted gas to filtered clean gas"
                    }
                  />
                  <span>
                    {progress < 58
                      ? "MEDICAL BAG DELIVERY"
                      : progress < 80
                        ? "GAS FILTRATION ACTIVE"
                        : "GAS FILTERED · BOTH ROBOTS RETURNING"}
                  </span>
                </div>
              )}
              {progress < 45 && (
                <div className="objective-icon victim">
                  <Icon name="target" size={26} />
                </div>
              )}
              <div className="brief-row">
                <span>MISSION UNITS</span>
                <b>MED-04 + GAS-09</b>
              </div>
              <div className="brief-row">
                <span>MED-04</span>
                <b>
                  {progress < 45
                    ? "TO VICTIM"
                    : progress < 58
                      ? "DROP MEDICAL BAG"
                      : "VICTIM SAFE / RETURN"}
                </b>
              </div>
              <div className="brief-row">
                <span>GAS-09</span>
                <b>
                  {progress < 58
                    ? "TO GAS LEAK"
                    : progress < 80
                      ? "FILTER + SEAL"
                      : "LEAK SAFE / RETURN"}
                </b>
              </div>
              <div className="progress-block">
                <div>
                  <span>MISSION PROGRESS</span>
                  <b>{progress}%</b>
                </div>
                <div className="bar">
                  <i style={{ width: `${progress}%` }} />
                </div>
              </div>
            </div>
          ) : (
            <div className="panel completion-card">
              <div className="completion-evidence">
                <figure>
                  <img
                    src={victimHelpedImage}
                    alt="Executor robot helping the victim with a medical aid bag"
                  />
                  <figcaption>VICTIM HELPED</figcaption>
                </figure>
                <figure>
                  <img
                    src={gasFilteredImage}
                    alt="Gas leak transformed from polluted gas to filtered clean gas"
                  />
                  <figcaption>GAS FILTERED</figcaption>
                </figure>
              </div>
              <div className="completion-copy">
                <Tag>RETURNED · ORIGIN 0,0</Tag>
                <h2>All Objectives Complete</h2>
                <p>
                  MED-04 delivered medical help and GAS-09 filtered and stopped
                  the leak. Both robots returned to origin.
                </p>
                <div className="reported">
                  <span className="status-dot" />
                  <span>
                    Reported to Command Post
                    <br />
                    <small>via ONA-01 · acknowledgement received</small>
                  </span>
                </div>
                <button className="secondary-action" onClick={onCommand}>
                  RETURN TO COMMAND POST
                </button>
              </div>
            </div>
          )}
        </aside>
      </div>
    </section>
  )
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("writer")

  const activeIndex = useMemo(
    () => tabs.findIndex((tab) => tab.id === screen),
    [screen],
  )

  return (
    <main className="app-shell">
      <header className="app-header">
        <button
          className="brand"
          onClick={() => setScreen("writer")}
          aria-label="The Living Map home"
        >
          <span className="brand-mark">
            <i />
            <i />
            <i />
          </span>
          <span>
            <b>THE LIVING MAP</b>
            <small>RESILIENT ROBOTIC RESPONSE SYSTEM</small>
          </span>
        </button>
        <nav className="tabs" aria-label="Mission screens">
          {tabs.map((tab, index) => (
            <button
              key={tab.id}
              className={
                screen === tab.id
                  ? "active"
                  : index < activeIndex
                    ? "visited"
                    : ""
              }
              onClick={() => setScreen(tab.id)}
            >
              <span>{tab.step}</span>
              <div>
                <b>{tab.label}</b>
                <small>{tab.meta}</small>
              </div>
            </button>
          ))}
        </nav>
        <div className="system-meta">
          <span>
            <i /> SYSTEM NOMINAL
          </span>
          <b>UTC 10:48:12</b>
          <small>TSYP14 / DEMO-01</small>
        </div>
      </header>

      {screen === "writer" && (
        <WriterView onContinue={() => setScreen("command")} />
      )}
      {screen === "command" && (
        <CommandView onDeploy={() => setScreen("executor")} />
      )}
      {screen === "executor" && (
        <ExecutorView onCommand={() => setScreen("command")} />
      )}

      <footer>
        <span>
          WRITER <i /> BEACONS <i /> ONA <i /> COMMAND POST <i /> EXECUTOR
        </span>
        <span>
          ENCRYPTED MESH / AES-256 <b>•</b> SESSION 7F2A
        </span>
      </footer>
    </main>
  )
}
