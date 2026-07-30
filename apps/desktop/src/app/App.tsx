import { useEffect, useMemo, useState } from "react";

import { CommandShell } from "./CommandShell";
import type {
  HealthScenario,
  HealthView,
  ScenarioId,
  ScenarioView,
} from "./contracts";
import { fetchHealth } from "./health";
import { fetchScenario } from "./scenario";
import { ScenarioLab } from "./ScenarioLab";

let pendingHealthRequest: Promise<HealthView> | null = null;
const pendingScenarioRequests = new Map<ScenarioId, Promise<ScenarioView>>();

function loadHealth(): Promise<HealthView> {
  if (pendingHealthRequest) {
    return pendingHealthRequest;
  }

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 4_000);
  pendingHealthRequest = fetchHealth(controller.signal).finally(() => {
    window.clearTimeout(timeout);
    pendingHealthRequest = null;
  });
  return pendingHealthRequest;
}

function loadScenario(scenario: ScenarioId): Promise<ScenarioView> {
  const pendingRequest = pendingScenarioRequests.get(scenario);
  if (pendingRequest) {
    return pendingRequest;
  }

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 4_000);
  const request = fetchScenario(scenario, controller.signal).finally(() => {
    window.clearTimeout(timeout);
    if (pendingScenarioRequests.get(scenario) === request) {
      pendingScenarioRequests.delete(scenario);
    }
  });
  pendingScenarioRequests.set(scenario, request);
  return request;
}

function requestedScenario(): HealthScenario | null {
  const value = new URLSearchParams(window.location.search).get("state");
  return value === "loading" ||
    value === "degraded" ||
    value === "stale" ||
    value === "error"
    ? value
    : null;
}

function withDegradedPostgres(view: HealthView): HealthView {
  return {
    ...view,
    status: "degraded",
    prerequisites: {
      ...view.prerequisites,
      postgresql: {
        status: "unavailable",
        detail:
          "Verification scenario: PostgreSQL readiness is intentionally unavailable.",
      },
    },
  };
}

const fixtureScenarios = new Set<ScenarioId>([
  "valid",
  "stale",
  "duplicate",
  "contradictory",
  "denied",
  "degraded",
  "timeout",
  "recovery",
]);

function requestedFixtureScenario(): ScenarioId | null {
  const value = new URLSearchParams(window.location.search).get("scenario");
  return fixtureScenarios.has(value as ScenarioId)
    ? (value as ScenarioId)
    : null;
}

function HealthRoute() {
  const forcedScenario = useMemo(requestedScenario, []);
  const [health, setHealth] = useState<HealthView | null>(null);
  const [scenario, setScenario] = useState<HealthScenario>(
    forcedScenario === "stale" ||
      forcedScenario === "loading" ||
      forcedScenario === "error"
      ? forcedScenario
      : "loading",
  );

  useEffect(() => {
    if (
      forcedScenario === "loading" ||
      forcedScenario === "stale" ||
      forcedScenario === "error"
    ) {
      return;
    }

    let isCurrent = true;

    loadHealth()
      .then((view) => {
        if (!isCurrent) {
          return;
        }
        setHealth(
          forcedScenario === "degraded" ? withDegradedPostgres(view) : view,
        );
        setScenario(
          forcedScenario ?? (view.status === "healthy" ? "live" : "degraded"),
        );
      })
      .catch(() => {
        if (!isCurrent) {
          return;
        }
        setHealth(null);
        setScenario("stale");
      });

    return () => {
      isCurrent = false;
    };
  }, [forcedScenario]);

  return <CommandShell health={health} scenario={scenario} />;
}

function ScenarioRoute({ initialScenario }: { initialScenario: ScenarioId }) {
  const [selectedScenario, setSelectedScenario] =
    useState<ScenarioId>(initialScenario);
  const [view, setView] = useState<ScenarioView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCurrent = true;
    setLoading(true);
    setView(null);
    setError(null);

    loadScenario(selectedScenario)
      .then((scenarioView) => {
        if (!isCurrent) {
          return;
        }
        setView(scenarioView);
        setLoading(false);
      })
      .catch(() => {
        if (!isCurrent) {
          return;
        }
        setView(null);
        setError("Scenario contract unavailable.");
        setLoading(false);
      });

    return () => {
      isCurrent = false;
    };
  }, [selectedScenario]);

  const selectScenario = (scenario: ScenarioId) => {
    const nextUrl = new URL(window.location.href);
    nextUrl.search = "";
    nextUrl.searchParams.set("scenario", scenario);
    window.history.replaceState({}, "", nextUrl);
    setSelectedScenario(scenario);
  };

  return (
    <ScenarioLab
      error={error}
      loading={loading}
      onSelect={selectScenario}
      view={view}
    />
  );
}

export function App() {
  const fixtureScenario = useMemo(requestedFixtureScenario, []);

  return fixtureScenario ? (
    <ScenarioRoute initialScenario={fixtureScenario} />
  ) : (
    <HealthRoute />
  );
}
