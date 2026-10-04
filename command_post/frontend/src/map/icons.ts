import L from "leaflet";

export function makeIcon(emoji: string, color = "#58a6ff"): L.DivIcon {
  return L.divIcon({
    className: "",
    html: `<div style="
      background:${color};
      width:26px;height:26px;border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      color:white;font-size:14px;
      box-shadow:0 0 0 2px rgba(0,0,0,0.5);">${emoji}</div>`,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
  });
}