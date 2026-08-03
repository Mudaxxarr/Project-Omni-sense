export function isViteHmrTransportError(message: string): boolean {
  return (
    message.startsWith("WebSocket connection to 'ws://127.0.0.1:4173/?token=") &&
    message.includes("net::ERR_NO_BUFFER_SPACE")
  );
}
