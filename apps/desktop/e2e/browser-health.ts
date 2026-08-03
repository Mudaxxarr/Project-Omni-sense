import type { APIResponse, Page } from "@playwright/test";

export function isViteHmrTransportError(message: string): boolean {
  return (
    message.startsWith("WebSocket connection to 'ws://127.0.0.1:4173/?token=") &&
    message.includes("net::ERR_NO_BUFFER_SPACE")
  );
}

export async function getLocalApiResponse(
  page: Page,
  url: string,
): Promise<APIResponse> {
  let lastError: unknown;

  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      return await page.request.get(url, { timeout: 5_000 });
    } catch (error) {
      lastError = error;
      if (attempt < 3) {
        await page.waitForTimeout(200);
      }
    }
  }

  throw lastError;
}
