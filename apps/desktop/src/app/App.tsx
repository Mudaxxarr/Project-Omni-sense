import { useEffect, useMemo, useState } from "react";

import { CommandShell } from "./CommandShell";
import type { HealthScenario, HealthView } from "./contracts";
import { fetchHealth } from "./health";

let pendingHealthRequest: Promise<HealthView> | null = null;

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

export function App() {
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
