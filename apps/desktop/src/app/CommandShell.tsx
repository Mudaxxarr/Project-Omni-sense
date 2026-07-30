import {
  Archive,
  Brain,
  CheckCircle,
  Clock,
  Database,
  HardDrive,
  House,
  LockKey,
  ShieldCheck,
  UsersThree,
  WarningCircle,
  X,
} from "@phosphor-icons/react";
import { useEffect, useId, useState } from "react";

import type {
  HealthScenario,
  HealthView,
  RequirementStatus,
  RequirementView,
} from "./contracts";

interface CommandShellProps {
  health: HealthView | null;
  scenario: HealthScenario;
}

const navigation = [
  { label: "Now", href: "#now", icon: House },
  { label: "Think", href: "#think", icon: Brain },
  { label: "People", href: "#people", icon: UsersThree },
  { label: "Memory", href: "#memory", icon: Archive },
] as const;

const requirementCopy = {
  core_api: {
    label: "Core API",
    phase: "Phase 0",
    icon: HardDrive,
  },
  postgresql: {
    label: "PostgreSQL 16",
    phase: "Phase 0",
    icon: Database,
  },
  evidence_vault: {
    label: "Evidence vault",
    phase: "Phase 1",
    icon: Archive,
  },
  audit_chain: {
    label: "Audit chain",
    phase: "Phase 1",
    icon: ShieldCheck,
  },
} as const;

function formatPktTime() {
  return new Intl.DateTimeFormat("en-PK", {
    timeZone: "Asia/Karachi",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date());
}

function statusLabel(status: RequirementStatus) {
  if (status === "ready") {
    return "Ready";
  }
  if (status === "planned") {
    return "Planned";
  }
  if (status === "not_configured") {
    return "Setup required";
  }
  return "Unavailable";
}

function RequirementRow({
  itemKey,
  requirement,
}: {
  itemKey: keyof typeof requirementCopy;
  requirement: RequirementView;
}) {
  const copy = requirementCopy[itemKey];
  const Icon = copy.icon;
  const healthy = requirement.status === "ready";

  return (
    <li className="requirement-row">
      <span className="requirement-icon" data-status={requirement.status}>
        <Icon aria-hidden="true" size={19} weight={healthy ? "fill" : "regular"} />
      </span>
      <span className="requirement-copy">
        <span className="requirement-title-line">
          <strong>{copy.label}</strong>
          <span>{copy.phase}</span>
        </span>
        <span className="requirement-detail">{requirement.detail}</span>
      </span>
      <span className="requirement-status" data-status={requirement.status}>
        {healthy ? (
          <CheckCircle aria-hidden="true" size={15} weight="fill" />
        ) : (
          <WarningCircle aria-hidden="true" size={15} weight="fill" />
        )}
        {statusLabel(requirement.status)}
      </span>
    </li>
  );
}

function SkeletonShell() {
  return (
    <div className="loading-panel" role="status" aria-live="polite">
      <span className="loading-mark" aria-hidden="true" />
      <p>Checking the local trust boundary</p>
      <span>Verifying the core API and native prerequisites…</span>
    </div>
  );
}

export function CommandShell({ health, scenario }: CommandShellProps) {
  const [isSetupOpen, setSetupOpen] = useState(false);
  const setupTitleId = useId();
  const isStale = scenario === "stale";
  const isError = scenario === "error";
  const isUnavailable = isStale || isError;
  const isLoading = scenario === "loading";
  const checkedTime = formatPktTime();

  useEffect(() => {
    if (!isSetupOpen) {
      return;
    }

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setSetupOpen(false);
      }
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [isSetupOpen]);

  const requirements = health?.prerequisites;
  const postgresReady = requirements?.postgresql.status === "ready";

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to command centre
      </a>

      <header className="topbar">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">
            O
          </span>
          <span translate="no">
            <strong>OMNISCIENCE</strong>
            <small>Owner intelligence</small>
          </span>
        </div>

        <div className="trust-strip" aria-label="Runtime trust status">
          <span className="local-badge">
            <LockKey aria-hidden="true" size={13} weight="bold" />
            Local only
          </span>
          <span className="topbar-divider" aria-hidden="true" />
          <span className="service-indicator" data-state={scenario}>
            <span aria-hidden="true" />
            {isLoading
              ? "Checking core"
              : isStale
                ? "Core unreachable"
                : isError
                  ? "Core error"
                  : "Core online"}
          </span>
          <span className="topbar-divider" aria-hidden="true" />
          <span className="pkt-time">
            <Clock aria-hidden="true" size={14} />
            {checkedTime} PKT
          </span>
        </div>
      </header>

      <aside className="sidebar">
        <nav aria-label="Owner spaces">
          <p className="nav-label">Spaces</p>
          <ul>
            {navigation.map((item, index) => {
              const Icon = item.icon;
              return (
                <li key={item.label}>
                  <a
                    className={index === 0 ? "nav-link active" : "nav-link"}
                    href={item.href}
                    aria-current={index === 0 ? "page" : undefined}
                  >
                    <Icon
                      aria-hidden="true"
                      size={19}
                      weight={index === 0 ? "fill" : "regular"}
                    />
                    <span>{item.label}</span>
                  </a>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="privacy-note">
          <ShieldCheck aria-hidden="true" size={19} weight="fill" />
          <div>
            <strong>Private by design</strong>
            <span>Local only. No data leaves this PC.</span>
          </div>
        </div>
      </aside>

      <main id="main-content" className="main-content">
        <section id="now" className="hero-row" aria-labelledby="page-title">
          <div>
            <p className="eyebrow">Command centre / Phase 0</p>
            <h1 id="page-title">Good evening, Mudassar.</h1>
            <p className="hero-copy">
              The local foundation is taking shape. Live business intelligence
              will remain locked until its source and evidence path are proven.
            </p>
          </div>
          <div className="phase-seal" aria-label="Phase 0 integration state">
            <span>01</span>
            <div>
              <small>Current gate</small>
              <strong>Local foundation</strong>
            </div>
          </div>
        </section>

        {isLoading ? (
          <SkeletonShell />
        ) : (
          <>
            <section
              className={
                isUnavailable ? "state-banner critical" : "state-banner"
              }
              aria-live="polite"
            >
              <span className="state-symbol" aria-hidden="true">
                {isUnavailable ? (
                  <WarningCircle size={22} weight="fill" />
                ) : (
                  <Database size={22} weight="fill" />
                )}
              </span>
              <div>
                <strong>
                  {isError
                    ? "Health check failed"
                    : isStale
                      ? "Data stale"
                      : "Data not connected"}
                </strong>
                <p>
                  {isError
                    ? "Local readiness could not be verified. Consequential controls are locked."
                    : isStale
                      ? "Data stale. Consequential controls are locked."
                      : postgresReady
                        ? "The local database is ready. Connect a read-only source in the next build gate."
                        : "PostgreSQL setup required"}
                </p>
              </div>
              <button
                className="primary-action"
                type="button"
                disabled={isUnavailable}
                onClick={() => setSetupOpen(true)}
              >
                Start source setup
              </button>
            </section>

            <div className="content-grid">
              <section className="readiness-panel" aria-labelledby="readiness-title">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">Foundation health</p>
                    <h2 id="readiness-title">Readiness ledger</h2>
                  </div>
                  <span className="ledger-timestamp">
                    {isUnavailable
                      ? "Last result unavailable"
                      : `Checked ${checkedTime} PKT`}
                  </span>
                </div>

                {requirements ? (
                  <ul className="requirement-list">
                    <RequirementRow
                      itemKey="core_api"
                      requirement={requirements.core_api}
                    />
                    <RequirementRow
                      itemKey="postgresql"
                      requirement={requirements.postgresql}
                    />
                    <RequirementRow
                      itemKey="evidence_vault"
                      requirement={requirements.evidence_vault}
                    />
                    <RequirementRow
                      itemKey="audit_chain"
                      requirement={requirements.audit_chain}
                    />
                  </ul>
                ) : (
                  <div className="unavailable-state">
                    <WarningCircle aria-hidden="true" size={24} />
                    <div>
                      <strong>Readiness evidence unavailable</strong>
                      <span>
                        {isError
                          ? "Correct the local health contract before continuing setup."
                          : "Restore the local core service before continuing setup."}
                      </span>
                    </div>
                  </div>
                )}
              </section>

              <aside className="insight-rail" aria-label="Phase 0 controls">
                <section>
                  <p className="eyebrow">Trust boundary</p>
                  <h2>No cloud inference</h2>
                  <p>
                    Phase 0 permits local runtime checks only. Operational data
                    connectors and AI inference are not enabled.
                  </p>
                  <dl>
                    <div>
                      <dt>Runtime</dt>
                      <dd>Native Windows</dd>
                    </div>
                    <div>
                      <dt>Timezone</dt>
                      <dd>Asia/Karachi</dd>
                    </div>
                    <div>
                      <dt>Contract</dt>
                      <dd>{health?.contract_version ?? "Unavailable"}</dd>
                    </div>
                  </dl>
                </section>

                <section className="next-gate">
                  <p className="eyebrow">Next integration gate</p>
                  <h2>Evidence foundation</h2>
                  <p>
                    Native database, audit chain, retention enforcement, and a
                    tested restore path.
                  </p>
                  <span>Phase 1</span>
                </section>
              </aside>
            </div>
          </>
        )}
      </main>

      <footer className="footer">
        <span>OMNISCIENCE 0.0.1</span>
        <span>Founder build ledger active</span>
      </footer>

      {isSetupOpen ? (
        <div className="dialog-backdrop" role="presentation">
          <section
            className="setup-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby={setupTitleId}
          >
            <button
              className="icon-button"
              type="button"
              aria-label="Close source setup"
              onClick={() => setSetupOpen(false)}
            >
              <X aria-hidden="true" size={18} />
            </button>
            <span className="dialog-icon" aria-hidden="true">
              <Database size={24} weight="fill" />
            </span>
            <p className="eyebrow">Source setup</p>
            <h2 id={setupTitleId}>Foundation first</h2>
            <p>
              Source onboarding unlocks after native PostgreSQL passes its local
              readiness check. This gate prevents evidence from entering an
              unproven storage path.
            </p>
            <div className="dialog-check">
              <span data-ready={postgresReady}>
                {postgresReady ? (
                  <CheckCircle aria-hidden="true" weight="fill" />
                ) : (
                  <WarningCircle aria-hidden="true" weight="fill" />
                )}
              </span>
              <div>
                <strong>
                  {postgresReady
                    ? "PostgreSQL is ready"
                    : "PostgreSQL setup required"}
                </strong>
                <small>
                  {requirements?.postgresql.detail ??
                    "The local core cannot report database readiness."}
                </small>
              </div>
            </div>
            <button
              className="secondary-action"
              type="button"
              onClick={() => setSetupOpen(false)}
            >
              Return to ledger
            </button>
          </section>
        </div>
      ) : null}
    </div>
  );
}
