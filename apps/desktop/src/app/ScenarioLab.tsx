import {
  ArrowLeft,
  ClockCounterClockwise,
  Database,
  Flask,
  LockKey,
  ShieldCheck,
  WarningCircle,
} from "@phosphor-icons/react";

import type {
  FixtureFamily,
  ScenarioId,
  ScenarioView,
} from "./contracts";

interface ScenarioLabProps {
  error: string | null;
  loading: boolean;
  onSelect: (scenario: ScenarioId) => void;
  view: ScenarioView | null;
}

const familyLabels: Record<FixtureFamily, string> = {
  users: "Users",
  roles: "Roles",
  financial_imports: "Financial imports",
  customers: "Customers",
  visits: "Visits",
  products: "Products",
  promises: "Promises",
  tasks: "Tasks",
  evidence: "Evidence",
  meetings: "Meetings",
  provider_responses: "Provider responses",
  model_outcomes: "Model outcomes",
};

function formatPktTime(isoTime: string) {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Karachi",
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(new Date(isoTime));
  const value = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((part) => part.type === type)?.value ?? "";

  return `${value("day")} ${value("month")} ${value("year")}, ${value("hour")}:${value("minute")} PKT`;
}

function LabFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="scenario-shell">
      <a className="skip-link" href="#scenario-main">
        Skip to scenario evidence
      </a>
      <header className="scenario-topbar">
        <a className="scenario-brand" href="/" aria-label="Return to Command Centre">
          <span aria-hidden="true">O</span>
          <strong translate="no">OMNISCIENCE</strong>
        </a>
        <div className="scenario-trust" aria-label="Scenario trust boundary">
          <span>
            <LockKey aria-hidden="true" size={14} weight="bold" />
            Local only
          </span>
          <span>
            <ShieldCheck aria-hidden="true" size={14} weight="fill" />
            Actions locked
          </span>
        </div>
      </header>
      {children}
    </div>
  );
}

function LockedAction({ reason }: { reason: string }) {
  return (
    <div className="scenario-lock">
      <div>
        <LockKey aria-hidden="true" size={18} weight="fill" />
        <span>{reason}</span>
      </div>
      <button type="button" disabled>
        Consequential actions locked
      </button>
    </div>
  );
}

export function ScenarioLab({
  error,
  loading,
  onSelect,
  view,
}: ScenarioLabProps) {
  if (loading && !view) {
    return (
      <LabFrame>
        <main id="scenario-main" className="scenario-main">
          <div className="scenario-loading" role="status">
            <span aria-hidden="true" />
            <h1>Loading deterministic fixture</h1>
            <p>Reading the committed local catalog and validating its contract.</p>
          </div>
          <LockedAction reason="Scenario evidence has not been verified." />
        </main>
      </LabFrame>
    );
  }

  if (error || !view) {
    return (
      <LabFrame>
        <main id="scenario-main" className="scenario-main">
          <div className="scenario-error" role="alert">
            <WarningCircle aria-hidden="true" size={26} weight="fill" />
            <div>
              <h1>Scenario evidence unavailable</h1>
              <p>{error ?? "The local scenario contract could not be read."}</p>
            </div>
          </div>
          <LockedAction reason="Missing fixture evidence cannot authorize action." />
        </main>
      </LabFrame>
    );
  }

  const entityFamilies = Object.entries(view.entities) as [
    FixtureFamily,
    ScenarioView["entities"][FixtureFamily],
  ][];

  return (
    <LabFrame>
      <main id="scenario-main" className="scenario-main">
        <div className="scenario-return">
          <a href="/">
            <ArrowLeft aria-hidden="true" size={15} />
            Command Centre
          </a>
          <span>Anonymized fixture data</span>
        </div>

        <section className="scenario-intro" aria-labelledby="scenario-title">
          <div>
            <p className="eyebrow">Phase 0 proof harness</p>
            <h1 id="scenario-title">Deterministic Scenario Lab</h1>
            <p>
              Inspect safe failure and recovery states against one fixed local
              fixture catalog.
            </p>
          </div>
          <dl className="scenario-summary">
            <div>
              <dt>Catalog</dt>
              <dd>{view.fixture_version}</dd>
            </div>
            <div>
              <dt>Coverage</dt>
              <dd>{view.summary.entity_family_count} entity families</dd>
            </div>
            <div>
              <dt>Records</dt>
              <dd>{view.summary.record_count} deterministic</dd>
            </div>
          </dl>
        </section>

        <nav className="scenario-selector" aria-label="Fixture scenarios">
          {view.available_scenarios.map((scenario) => (
            <button
              key={scenario.id}
              type="button"
              aria-pressed={scenario.id === view.scenario.id}
              data-status={scenario.status}
              onClick={() => onSelect(scenario.id)}
            >
              {scenario.label}
            </button>
          ))}
        </nav>

        <section
          className="scenario-state"
          data-status={view.scenario.status}
          aria-labelledby="scenario-state-title"
          aria-live="polite"
        >
          <div className="scenario-state-heading">
            <span aria-hidden="true">
              <Flask size={22} weight="fill" />
            </span>
            <div>
              <p>{view.scenario.label} scenario</p>
              <h2 id="scenario-state-title">{view.scenario.headline}</h2>
            </div>
          </div>
          <p>{view.scenario.detail}</p>
          <ul aria-label="Scenario signals">
            {view.signals.map((signal) => (
              <li key={signal}>{signal}</li>
            ))}
          </ul>
        </section>

        <div className="scenario-evidence-grid">
          <section className="scenario-time" aria-labelledby="clock-title">
            <div className="scenario-section-heading">
              <ClockCounterClockwise aria-hidden="true" size={20} />
              <div>
                <h2 id="clock-title">Deterministic clock</h2>
                <p>One instant, two explicit representations.</p>
              </div>
            </div>
            <dl>
              <div>
                <dt>Stored in UTC</dt>
                <dd>{view.clock.stored_at_utc}</dd>
              </div>
              <div>
                <dt>Shown to owner</dt>
                <dd>{formatPktTime(view.clock.displayed_at_local)}</dd>
              </div>
              <div>
                <dt>Timezone rule</dt>
                <dd>{view.clock.timezone}</dd>
              </div>
            </dl>
          </section>

          <section className="scenario-fixtures" aria-labelledby="fixtures-title">
            <div className="scenario-section-heading">
              <Database aria-hidden="true" size={20} />
              <div>
                <h2 id="fixtures-title">Fixture coverage</h2>
                <p>Every Phase 0 entity family is present and countable.</p>
              </div>
            </div>
            <div className="fixture-family-grid">
              {entityFamilies.map(([family, records]) => (
                <div key={family} data-family={family}>
                  <span>{familyLabels[family]}</span>
                  <strong>{records.length}</strong>
                </div>
              ))}
            </div>
          </section>
        </div>

        <LockedAction reason={view.action_lock_reason} />
      </main>
    </LabFrame>
  );
}
