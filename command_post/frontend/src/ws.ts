import type { WsMessage } from "./types";

export function connectWS(
  onMessage: (msg: WsMessage) => void,
): () => void {
  const url = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";
  let ws: WebSocket | null = null;
  let closed = false;
  let retry = 1000;

  const open = () => {
    if (closed) return;
    ws = new WebSocket(url);
    ws.onopen = () => { retry = 1000; };
    ws.onmessage = (e) => {
      try {
        onMessage(JSON.parse(e.data));
      } catch (err) {
        console.warn("bad ws message", err);
      }
    };
    ws.onclose = () => {
      if (closed) return;
      setTimeout(open, retry);
      retry = Math.min(retry * 2, 10000);
    };
    ws.onerror = () => ws?.close();
  };

  open();
  return () => {
    closed = true;
    ws?.close();
  };
}