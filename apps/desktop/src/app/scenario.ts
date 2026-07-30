import type { ScenarioId, ScenarioView } from "./contracts";

const DEFAULT_CORE_API = "http://127.0.0.1:8765";

export async function fetchScenario(
  scenario: ScenarioId,
  signal: AbortSignal,
): Promise<ScenarioView> {
  const apiBase = import.meta.env.VITE_CORE_API_URL ?? DEFAULT_CORE_API;
  const response = await fetch(
    `${apiBase}/v1/scenarios/${encodeURIComponent(scenario)}`,
    {
      headers: {
        Accept: "application/json",
      },
      signal,
    },
  );

  if (!response.ok) {
    throw new Error(`Scenario request failed with status ${response.status}.`);
  }

  return (await response.json()) as ScenarioView;
}
