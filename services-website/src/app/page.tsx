"use client";

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Download,
  LoaderCircle,
  RefreshCw,
  Server,
  ShieldAlert,
  Sparkles,
  XCircle,
} from "lucide-react";
import {
  FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";


const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";


type IncidentStatus =
  | "queued"
  | "processing"
  | "completed"
  | "failed";

type Severity =
  | "low"
  | "medium"
  | "high"
  | "critical";


type IncidentAnalysis = {
  root_cause: string;
  affected_services: string[];
  severity: Severity;
  fix_recommendation: string;
  postmortem_summary: string;
};


type Incident = {
  id: number;
  status: IncidentStatus;
  job_id: string | null;
  created_at: string;
  updated_at: string;
  analysis: IncidentAnalysis | null;
  error_message: string | null;
};


type IncidentForm = {
  logs: string;
  stack_trace: string;
  metrics: string;
};


const emptyForm: IncidentForm = {
  logs: "",
  stack_trace: "",
  metrics: "",
};


function statusClass(status: IncidentStatus) {
  return `status status-${status}`;
}


function severityClass(severity?: Severity) {
  if (!severity) return "severity severity-unknown";

  return `severity severity-${severity}`;
}


function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}


function IncidentStatusIcon({
  status,
}: {
  status: IncidentStatus;
}) {
  if (status === "completed") {
    return <CheckCircle2 size={16} />;
  }

  if (status === "failed") {
    return <XCircle size={16} />;
  }

  if (status === "processing") {
    return (
      <LoaderCircle
        size={16}
        className="spin"
      />
    );
  }

  return <Clock3 size={16} />;
}


export default function Home() {
  const [incidents, setIncidents] =
    useState<Incident[]>([]);

  const [selectedId, setSelectedId] =
    useState<number | null>(null);

  const [form, setForm] =
    useState<IncidentForm>(emptyForm);

  const [loading, setLoading] =
    useState(true);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  const loadIncidents = useCallback(
    async (silent = false) => {
      if (!silent) {
        setLoading(true);
      }

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/v1/incidents?limit=50`,
          {
            cache: "no-store",
          }
        );

        if (!response.ok) {
          throw new Error(
            `API returned ${response.status}`
          );
        }

        const data: Incident[] =
          await response.json();

        setIncidents(data);
        setError(null);

        setSelectedId((current) => {
          if (
            current !== null &&
            data.some(
              (incident) =>
                incident.id === current
            )
          ) {
            return current;
          }

          return data[0]?.id ?? null;
        });
      } catch {
        setError(
          "Unable to connect to the incident analysis API."
        );
      } finally {
        if (!silent) {
          setLoading(false);
        }
      }
    },
    []
  );


  useEffect(() => {
    loadIncidents();
  }, [loadIncidents]);


  const hasActiveJobs = useMemo(
    () =>
      incidents.some(
        (incident) =>
          incident.status === "queued" ||
          incident.status === "processing"
      ),
    [incidents]
  );


  useEffect(() => {
    if (!hasActiveJobs) {
      return;
    }

    const interval = window.setInterval(
      () => {
        loadIncidents(true);
      },
      2000
    );

    return () => {
      window.clearInterval(interval);
    };
  }, [
    hasActiveJobs,
    loadIncidents,
  ]);


  const selectedIncident =
    incidents.find(
      (incident) =>
        incident.id === selectedId
    ) ?? null;


  const stats = useMemo(() => {
    return {
      total: incidents.length,

      active: incidents.filter(
        (incident) =>
          incident.status === "queued" ||
          incident.status === "processing"
      ).length,

      critical: incidents.filter(
        (incident) =>
          incident.analysis?.severity ===
          "critical"
      ).length,

      completed: incidents.filter(
        (incident) =>
          incident.status === "completed"
      ).length,
    };
  }, [incidents]);


  async function submitIncident(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!form.logs.trim()) {
      setError(
        "Logs are required before analysis can start."
      );
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/incidents/analyze`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify(form),
        }
      );

      if (!response.ok) {
        throw new Error(
          `API returned ${response.status}`
        );
      }

      const incident: Incident =
        await response.json();

      setForm(emptyForm);

      await loadIncidents(true);

      setSelectedId(incident.id);
    } catch {
      setError(
        "The incident could not be submitted. Check the API and worker."
      );
    } finally {
      setSubmitting(false);
    }
  }


  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <Activity size={22} />
          </div>

          <div>
            <p className="eyebrow">
              Incident Intelligence
            </p>

            <h1>
              Root Cause Analyzer
            </h1>
          </div>
        </div>

        <div className="system-state">
          <span className="live-dot" />
          API connected
        </div>
      </header>


      <section className="hero">
        <div>
          <p className="eyebrow">
            AI-assisted production operations
          </p>

          <h2>
            Turn noisy incidents into
            actionable root causes.
          </h2>

          <p className="hero-copy">
            Correlate logs, stack traces,
            and runtime metrics through an
            asynchronous analysis pipeline
            backed by PostgreSQL, Redis,
            and background workers.
          </p>
        </div>

        <div className="architecture-pill">
          FastAPI
          <span>→</span>
          Redis
          <span>→</span>
          RQ Worker
          <span>→</span>
          PostgreSQL
        </div>
      </section>


      <section className="stats-grid">
        <StatCard
          icon={<Server size={20} />}
          label="Incidents"
          value={stats.total}
        />

        <StatCard
          icon={<LoaderCircle size={20} />}
          label="Active"
          value={stats.active}
        />

        <StatCard
          icon={<ShieldAlert size={20} />}
          label="Critical"
          value={stats.critical}
        />

        <StatCard
          icon={<CheckCircle2 size={20} />}
          label="Completed"
          value={stats.completed}
        />
      </section>


      {error && (
        <div className="error-banner">
          <AlertTriangle size={18} />
          {error}
        </div>
      )}


      <section className="workspace">
        <div className="panel incident-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">
                Incident queue
              </p>

              <h3>
                Recent incidents
              </h3>
            </div>

            <button
              className="icon-button"
              onClick={() =>
                loadIncidents()
              }
              aria-label="Refresh incidents"
            >
              <RefreshCw
                size={17}
                className={
                  loading
                    ? "spin"
                    : ""
                }
              />
            </button>
          </div>


          <div className="incident-list">
            {loading &&
              incidents.length === 0 && (
                <div className="empty-state">
                  Loading incidents...
                </div>
              )}

            {!loading &&
              incidents.length === 0 && (
                <div className="empty-state">
                  No incidents yet. Submit
                  one to start analysis.
                </div>
              )}

            {incidents.map(
              (incident) => (
                <button
                  key={incident.id}
                  className={`incident-row ${
                    selectedId ===
                    incident.id
                      ? "incident-row-active"
                      : ""
                  }`}
                  onClick={() =>
                    setSelectedId(
                      incident.id
                    )
                  }
                >
                  <div className="incident-row-top">
                    <span className="incident-id">
                      INC-
                      {String(
                        incident.id
                      ).padStart(
                        4,
                        "0"
                      )}
                    </span>

                    <span
                      className={statusClass(
                        incident.status
                      )}
                    >
                      <IncidentStatusIcon
                        status={
                          incident.status
                        }
                      />

                      {
                        incident.status
                      }
                    </span>
                  </div>

                  <div className="incident-row-bottom">
                    <span
                      className={severityClass(
                        incident.analysis
                          ?.severity
                      )}
                    >
                      {incident.analysis
                        ?.severity ??
                        "pending"}
                    </span>

                    <span className="incident-time">
                      {formatDate(
                        incident.created_at
                      )}
                    </span>
                  </div>
                </button>
              )
            )}
          </div>
        </div>


        <div className="panel detail-panel">
          {selectedIncident ? (
            <IncidentDetail
              incident={
                selectedIncident
              }
            />
          ) : (
            <div className="detail-empty">
              <Sparkles size={30} />

              <h3>
                Select an incident
              </h3>

              <p>
                Analysis results,
                remediation guidance,
                and postmortem data will
                appear here.
              </p>
            </div>
          )}
        </div>
      </section>


      <section className="panel submit-panel">
        <div className="panel-header submit-header">
          <div>
            <p className="eyebrow">
              New analysis
            </p>

            <h3>
              Analyze production telemetry
            </h3>
          </div>

          <span className="async-label">
            Async processing enabled
          </span>
        </div>


        <form
          className="incident-form"
          onSubmit={submitIncident}
        >
          <label>
            <span>
              Application logs
            </span>

            <textarea
              value={form.logs}
              onChange={(event) =>
                setForm({
                  ...form,
                  logs:
                    event.target.value,
                })
              }
              placeholder="ERROR payment-api connection pool exhausted..."
              required
            />
          </label>

          <label>
            <span>
              Stack trace
            </span>

            <textarea
              value={
                form.stack_trace
              }
              onChange={(event) =>
                setForm({
                  ...form,
                  stack_trace:
                    event.target.value,
                })
              }
              placeholder="TimeoutError: failed to acquire database connection..."
            />
          </label>

          <label className="metrics-field">
            <span>
              Runtime metrics
            </span>

            <textarea
              value={form.metrics}
              onChange={(event) =>
                setForm({
                  ...form,
                  metrics:
                    event.target.value,
                })
              }
              placeholder="db_pool=100%, error_rate=37%, p95_latency=4600ms"
            />
          </label>

          <div className="form-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                setForm(emptyForm)
              }
            >
              Clear
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <LoaderCircle
                    size={17}
                    className="spin"
                  />
                  Submitting...
                </>
              ) : (
                <>
                  <Sparkles
                    size={17}
                  />
                  Analyze incident
                </>
              )}
            </button>
          </div>
        </form>
      </section>


      <footer>
        AI Incident Root Cause Analyzer
        <span>•</span>
        Production-style SRE engineering project
      </footer>
    </main>
  );
}


function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {
  return (
    <div className="stat-card">
      <div className="stat-icon">
        {icon}
      </div>

      <div>
        <strong>{value}</strong>
        <span>{label}</span>
      </div>
    </div>
  );
}


function IncidentDetail({
  incident,
}: {
  incident: Incident;
}) {
  const analysis =
    incident.analysis;

  return (
    <>
      <div className="detail-heading">
        <div>
          <p className="eyebrow">
            Incident details
          </p>

          <h3>
            INC-
            {String(
              incident.id
            ).padStart(
              4,
              "0"
            )}
          </h3>
        </div>

        <span
          className={statusClass(
            incident.status
          )}
        >
          <IncidentStatusIcon
            status={
              incident.status
            }
          />
          {incident.status}
        </span>
      </div>


      {incident.status ===
        "failed" && (
        <div className="failed-box">
          <XCircle size={20} />

          <div>
            <strong>
              Analysis failed
            </strong>

            <p>
              {incident.error_message ??
                "Unknown worker error."}
            </p>
          </div>
        </div>
      )}


      {(incident.status ===
        "queued" ||
        incident.status ===
          "processing") && (
        <div className="processing-box">
          <LoaderCircle
            size={28}
            className="spin"
          />

          <div>
            <strong>
              Analysis in progress
            </strong>

            <p>
              The API has accepted this
              incident and the background
              worker is processing it.
            </p>
          </div>
        </div>
      )}


      {analysis && (
        <div className="analysis-content">
          <div className="analysis-block root-cause-block">
            <div className="analysis-label-row">
              <span className="analysis-label">
                Probable root cause
              </span>

              <span
                className={severityClass(
                  analysis.severity
                )}
              >
                {analysis.severity}
              </span>
            </div>

            <p className="root-cause">
              {analysis.root_cause}
            </p>
          </div>


          <div className="analysis-block">
            <span className="analysis-label">
              Affected services
            </span>

            <div className="service-list">
              {analysis.affected_services.map(
                (service) => (
                  <span
                    key={service}
                    className="service-chip"
                  >
                    {service}
                  </span>
                )
              )}
            </div>
          </div>


          <div className="analysis-block">
            <span className="analysis-label">
              Recommended remediation
            </span>

            <p>
              {
                analysis.fix_recommendation
              }
            </p>
          </div>


          <div className="analysis-block">
            <span className="analysis-label">
              Postmortem summary
            </span>

            <p>
              {
                analysis.postmortem_summary
              }
            </p>
          </div>


          <a
            className="download-button"
            href={`${API_BASE_URL}/api/v1/incidents/${incident.id}/pdf`}
            target="_blank"
            rel="noreferrer"
          >
            <Download size={17} />
            Download incident report
          </a>
        </div>
      )}
    </>
  );
}
