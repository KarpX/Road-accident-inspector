import { useState, useEffect, useCallback, useRef } from "react";
import "./App.css";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

import logo from "./assets/Logo.svg";

// ─── API ──────────────────────────────────────────────────────────────────────
const BASE = "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Ошибка ${res.status}`);
  }
  return res.json();
}

// ─── Types ────────────────────────────────────────────────────────────────────
interface Driver {
  id: number;
  full_name: string;
  driver_exp: number;
  driver_license: string;
}
interface Car {
  id: number;
  mark: string;
  number_plate: string;
  firm_id: number | null;
  body_type_id: number | null;
}
interface Department {
  id: number;
  name: string;
}
interface ActType {
  id: number;
  name: string;
}
interface ActReason {
  id: number;
  name: string;
}
interface Firm {
  id: number;
  name: string;
}
interface Body {
  id: number;
  name: string;
}
interface Participant {
  id: number;
  driver: Driver;
  car: Car;
}
interface Act {
  id: number;
  place: string;
  victims: number;
  date: string;
  department: Department;
  accident_type: ActType;
  accident_reason: ActReason;
  participants: Participant[];
}
interface ReasonStat {
  reason: string;
  count: number;
}

// ─── Icons ────────────────────────────────────────────────────────────────────
const IconHeader = () => {
  return <img src={logo} alt="Логотип ДТП Инспектор"></img>;
};
const IconHome = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
);
const IconDoc = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
  </svg>
);
const IconUser = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);
const IconCar = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect x="1" y="3" width="15" height="13" rx="2" />
    <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
    <circle cx="5.5" cy="18.5" r="2.5" />
    <circle cx="18.5" cy="18.5" r="2.5" />
  </svg>
);
const IconSettings = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="3" />
    <path d="M19.07 4.93a10 10 0 010 14.14M4.93 4.93a10 10 0 000 14.14" />
    <path d="M12 2v2M12 20v2M2 12h2M20 12h2" />
  </svg>
);
const IconLogout = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
    <polyline points="16 17 21 12 16 7" />
    <line x1="21" y1="12" x2="9" y2="12" />
  </svg>
);
const IconEdit = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
  </svg>
);
const IconTrash = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" />
    <path d="M10 11v6M14 11v6" />
    <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" />
  </svg>
);
const IconSearch = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);
const IconPlus = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.5"
    strokeLinecap="round"
  >
    <line x1="12" y1="5" x2="12" y2="19" />
    <line x1="5" y1="12" x2="19" y2="12" />
  </svg>
);
const IconClose = () => (
  <svg
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
  >
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

// ─── Toast ────────────────────────────────────────────────────────────────────
function Toast({
  msg,
  type,
  onDone,
}: {
  msg: string;
  type: "success" | "error";
  onDone: () => void;
}) {
  useEffect(() => {
    const t = setTimeout(onDone, 3000);
    return () => clearTimeout(t);
  }, [onDone]);
  return (
    <div className={`toast ${type}`}>
      {type === "success" ? "✓" : "✗"} {msg}
    </div>
  );
}

// ─── Confirm modal ────────────────────────────────────────────────────────────
function Confirm({
  msg,
  onConfirm,
  onCancel,
}: {
  msg: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div
        className="modal"
        style={{ maxWidth: 380 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-title" style={{ marginBottom: 12 }}>
          Подтверждение
        </div>
        <p style={{ fontSize: 15, color: "var(--gray-500)", marginBottom: 24 }}>
          {msg}
        </p>
        <div className="modal-actions">
          <button className="btn btn-outline" onClick={onCancel}>
            Отмена
          </button>
          <button
            className="btn btn-primary"
            style={{ background: "var(--red)" }}
            onClick={onConfirm}
          >
            Удалить
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Login Page ───────────────────────────────────────────────────────────────
function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [tab, setTab] = useState<"login" | "register">("login");
  const [key, setKey] = useState("");
  const [pass, setPass] = useState("");
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin() {
    setLoading(true);
    setError("");
    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", pass);
      const data = await apiFetch<{ access_token: string }>("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString(),
      });
      localStorage.setItem("token", data.access_token);
      onLogin();
    } catch (e: any) {
      setError(e.message);
    }
    setLoading(false);
  }

  async function handleRegister() {
    setLoading(true);
    setError("");
    try {
      const data = await apiFetch<{ access_token: string }>(
        "/api/auth/register",
        {
          method: "POST",
          body: JSON.stringify({ inspector_key: key, password: pass }),
        },
      );
      localStorage.setItem("token", data.access_token);
      onLogin();
    } catch (e: any) {
      setError(e.message);
    }
    setLoading(false);
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">
          <IconHeader />
          <p>Система учёта дорожных происшествий</p>
        </div>

        <div className="login-tabs">
          <button
            className={`login-tab ${tab === "login" ? "active" : ""}`}
            onClick={() => {
              setTab("login");
              setError("");
            }}
          >
            Войти
          </button>
          <button
            className={`login-tab ${tab === "register" ? "active" : ""}`}
            onClick={() => {
              setTab("register");
              setError("");
            }}
          >
            Регистрация
          </button>
        </div>

        {tab === "login" ? (
          <>
            <div className="form-group">
              <label className="form-label">Имя пользователя (ключ)</label>
              <input
                className="form-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="MVD-2024-XXXXXXXXXXXXXXXX"
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Пароль</label>
              <input
                className="form-input"
                type="password"
                value={pass}
                onChange={(e) => setPass(e.target.value)}
                placeholder="••••••••"
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              />
            </div>
            {error && <p className="form-error">{error}</p>}
            <button
              className="btn btn-primary"
              style={{ width: "100%", justifyContent: "center", marginTop: 8 }}
              onClick={handleLogin}
              disabled={loading}
            >
              {loading ? "Вход..." : "Войти"}
            </button>
          </>
        ) : (
          <>
            <div className="form-group">
              <label className="form-label">Инспекторский ключ</label>
              <input
                className="form-input"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="MVD-2024-XXXXXXXXXXXXXXXX"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Придумайте пароль</label>
              <input
                className="form-input"
                type="password"
                value={pass}
                onChange={(e) => setPass(e.target.value)}
                placeholder="••••••••"
              />
            </div>
            {error && <p className="form-error">{error}</p>}
            <button
              className="btn btn-primary"
              style={{ width: "100%", justifyContent: "center", marginTop: 8 }}
              onClick={handleRegister}
              disabled={loading}
            >
              {loading ? "Регистрация..." : "Зарегистрироваться"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

// ─── Sidebar ──────────────────────────────────────────────────────────────────
type Page = "dashboard" | "acts" | "drivers" | "cars";

function Sidebar({
  page,
  setPage,
  onLogout,
}: {
  page: Page;
  setPage: (p: Page) => void;
  onLogout: () => void;
}) {
  const nav = [
    { id: "dashboard" as Page, label: "Главная", icon: <IconHome /> },
    { id: "acts" as Page, label: "Акты", icon: <IconDoc /> },
    { id: "drivers" as Page, label: "Водители", icon: <IconUser /> },
    { id: "cars" as Page, label: "Автомобили", icon: <IconCar /> },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">
          <IconHeader />
        </div>
      </div>
      <nav className="sidebar-nav">
        {nav.map((n) => (
          <button
            key={n.id}
            className={`nav-item ${page === n.id ? "active" : ""}`}
            onClick={() => setPage(n.id)}
          >
            {n.icon} {n.label}
          </button>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <button className="nav-item" style={{ color: "var(--gray-400)" }}>
          <IconSettings /> Настройки
        </button>
        <button
          className="nav-item"
          style={{ color: "var(--red)" }}
          onClick={onLogout}
        >
          <IconLogout /> Выход
        </button>
      </div>
    </div>
  );
}

// ─── Dashboard ────────────────────────────────────────────────────────────────
function DashboardPage() {
  const [repeatOffenders, setRepeatOffenders] = useState<
    (Driver & { count?: number })[]
  >([]);
  const [pedestrians, setPedestrians] = useState<Driver[]>([]);
  const [reasonStats, setReasonStats] = useState<ReasonStat[]>([]);
  const [acts, setActs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<Driver[]>("/api/analytics/repeat-offenders"),
      apiFetch<Driver[]>("/api/analytics/pedestrian-accidents"),
      apiFetch<ReasonStat[]>("/api/analytics/reason-stats"),
      apiFetch<any[]>("/api/acts/"),
    ])
      .then(([ro, ped, rs, a]) => {
        setRepeatOffenders(ro);
        setPedestrians(ped);
        setReasonStats(rs.filter((r) => r.count > 0));
        setActs(a);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Build monthly chart data
  const monthlyData = (() => {
    const months = [
      "Янв",
      "Фев",
      "Мар",
      "Апр",
      "Май",
      "Июн",
      "Июл",
      "Авг",
      "Сен",
      "Окт",
      "Ноя",
      "Дек",
    ];
    const counts = new Array(12).fill(0);
    acts.forEach((a: any) => {
      const m = new Date(a.date).getMonth();
      counts[m]++;
    });
    return months.map((m, i) => ({ name: m, value: counts[i] }));
  })();

  const totalVictims = acts.reduce(
    (s: number, a: any) => s + (a.victims || 0),
    0,
  );

  const PIE_COLORS = [
    "#2563EB",
    "#10B981",
    "#F59E0B",
    "#EF4444",
    "#8B5CF6",
    "#06B6D4",
  ];

  if (loading)
    return (
      <div className="loader">
        <div className="spinner" /> Загрузка данных...
      </div>
    );

  return (
    <div className="page">
      <h1 className="page-title">Статистика</h1>

      <div className="stats-grid">
        {[
          {
            label: "Всего ДТП",
            value: acts.length.toLocaleString("ru"),
            icon: "💥",
            delta: "+8.5%",
            up: true,
          },
          {
            label: "Пострадавшие",
            value: totalVictims.toLocaleString("ru"),
            icon: "🚶",
            delta: "-1.5%",
            up: false,
          },
          {
            label: "Участвовало ТС",
            value: Math.round(acts.length * 1.2).toLocaleString("ru"),
            icon: "🚗",
            delta: "+2.4%",
            up: true,
          },
          {
            label: "Повторные ДТП",
            value: repeatOffenders.length.toLocaleString("ru"),
            icon: "⚠️",
            delta: "+1.2%",
            up: true,
          },
        ].map((s) => (
          <div className="card stat-card" key={s.label}>
            <div className="stat-label">{s.label}</div>
            <div className="stat-row">
              <div className="stat-value">{s.value}</div>
              <div className="stat-icon">{s.icon}</div>
            </div>
            <div className={`stat-delta ${s.up ? "up" : "down"}`}>
              {s.up ? "↑" : "↓"} {s.delta}
            </div>
          </div>
        ))}
      </div>

      <div className="card chart-card" style={{ marginBottom: 20 }}>
        <div className="chart-header">
          <div className="chart-title">Дорожно-транспортные происшествия</div>
          <select
            className="filter-select"
            style={{ width: "auto", padding: "6px 32px 6px 12px" }}
          >
            <option>Год</option>
            <option>Квартал</option>
            <option>Месяц</option>
          </select>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart
            data={monthlyData}
            margin={{ top: 5, right: 20, left: -20, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 12, fill: "#94A3B8" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#94A3B8" }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                borderRadius: 10,
                border: "1px solid #E2E8F0",
                boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
              }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#2563EB"
              strokeWidth={2.5}
              dot={{ fill: "#2563EB", r: 4 }}
              activeDot={{ r: 6 }}
              fill="rgba(37,99,235,0.08)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="stats-row2">
        <div className="card stat-card2">
          <div className="stat-card2-title">Повторные нарушения</div>
          {repeatOffenders.length === 0 ? (
            <div className="empty" style={{ padding: "20px 0" }}>
              <p>Нет данных</p>
            </div>
          ) : (
            <ul className="ranked-list">
              {repeatOffenders.slice(0, 5).map((d, i) => (
                <li key={d.id}>
                  <span className="rank-num">{i + 1}</span>
                  {d.full_name}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="card stat-card2">
          <div className="stat-card2-title">Наезд на пешехода</div>
          {pedestrians.length === 0 ? (
            <div className="empty" style={{ padding: "20px 0" }}>
              <p>Нет данных</p>
            </div>
          ) : (
            <ul className="ranked-list">
              {pedestrians.slice(0, 5).map((d, i) => (
                <li key={d.id}>
                  <span className="rank-num">{i + 1}</span>
                  {d.full_name}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="card stat-card2">
          <div className="stat-card2-title">Причины ДТП</div>
          {reasonStats.length === 0 ? (
            <div className="empty" style={{ padding: "20px 0" }}>
              <p>Нет данных</p>
            </div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={reasonStats}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    dataKey="count"
                    paddingAngle={3}
                  >
                    {reasonStats.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v, n, p) => [v, p.payload.reason]} />
                </PieChart>
              </ResponsiveContainer>
              <div
                style={{ fontSize: 12, color: "var(--gray-500)", marginTop: 8 }}
              >
                {reasonStats.slice(0, 3).map((r, i) => (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      marginBottom: 4,
                    }}
                  >
                    <span
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: 3,
                        background: PIE_COLORS[i],
                        flexShrink: 0,
                      }}
                    />
                    <span
                      style={{
                        flex: 1,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {r.reason}
                    </span>
                    <span style={{ fontWeight: 700, fontFamily: "monospace" }}>
                      {r.count}
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Acts Page ────────────────────────────────────────────────────────────────
function ActsPage() {
  const [acts, setActs] = useState<Act[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editAct, setEditAct] = useState<Act | null>(null);
  const [confirmId, setConfirmId] = useState<number | null>(null);
  const [toast, setToast] = useState<{
    msg: string;
    type: "success" | "error";
  } | null>(null);

  // Filters
  const [filterDateFrom, setFilterDateFrom] = useState("2026-01-01");
  const [filterDateTo, setFilterDateTo] = useState("2027-01-01");
  const [filterPlace, setFilterPlace] = useState("");
  const [filterType, setFilterType] = useState("");
  const [filterDept, setFilterDept] = useState("");

  // Dicts
  const [types, setTypes] = useState<ActType[]>([]);
  const [reasons, setReasons] = useState<ActReason[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [cars, setCars] = useState<Car[]>([]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [a, t, r, d, dr, ca] = await Promise.all([
        apiFetch<Act[]>("/api/acts/"),
        apiFetch<ActType[]>("/api/additional/accident/types"),
        apiFetch<ActReason[]>("/api/additional/accident/reasons"),
        apiFetch<Department[]>("/api/additional/departments/").catch(
          () => [] as Department[],
        ),
        apiFetch<Driver[]>("/api/drivers/"),
        apiFetch<Car[]>("/api/cars/"),
      ]);
      setActs(a);
      setTypes(t);
      setReasons(r);
      setDepartments(d);
      setDrivers(dr);
      setCars(ca);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = acts.filter((a) => {
    const date = new Date(a.date);
    if (filterDateFrom && date < new Date(filterDateFrom)) return false;
    if (filterDateTo && date > new Date(filterDateTo)) return false;
    if (
      filterPlace &&
      !a.place.toLowerCase().includes(filterPlace.toLowerCase())
    )
      return false;
    if (filterType && a.accident_type.id.toString() !== filterType)
      return false;
    if (filterDept && a.department.id.toString() !== filterDept) return false;
    return true;
  });

  async function handleDelete(id: number) {
    try {
      await apiFetch(`/api/acts/${id}`, { method: "DELETE" });
      setToast({ msg: "Акт удалён", type: "success" });
      load();
    } catch (e: any) {
      setToast({ msg: e.message, type: "error" });
    }
    setConfirmId(null);
  }

  return (
    <div className="page">
      <h1 className="page-title">Акты</h1>
      <div className="content-layout">
        <div className="filters-panel">
          <div className="card filter-card">
            <div className="section-add-btn">
              <button
                className="btn btn-primary"
                style={{ width: "100%", justifyContent: "center" }}
                onClick={() => {
                  setEditAct(null);
                  setShowModal(true);
                }}
              >
                <IconPlus /> Новый акт
              </button>
            </div>
            <div className="filter-section">
              <div className="filter-label">Период</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span
                    style={{
                      fontSize: 13,
                      color: "var(--gray-400)",
                      minWidth: 16,
                    }}
                  >
                    С
                  </span>
                  <input
                    type="date"
                    className="filter-input"
                    value={filterDateFrom}
                    onChange={(e) => setFilterDateFrom(e.target.value)}
                  />
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span
                    style={{
                      fontSize: 13,
                      color: "var(--gray-400)",
                      minWidth: 16,
                    }}
                  >
                    По
                  </span>
                  <input
                    type="date"
                    className="filter-input"
                    value={filterDateTo}
                    onChange={(e) => setFilterDateTo(e.target.value)}
                  />
                </div>
              </div>
            </div>
            <div className="filter-section">
              <div className="filter-label">Место</div>
              <input
                className="filter-input"
                placeholder="Место аварии..."
                value={filterPlace}
                onChange={(e) => setFilterPlace(e.target.value)}
              />
            </div>
            <div className="filter-section">
              <div className="filter-label">Вид ДТП</div>
              <select
                className="filter-select"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="">Все виды</option>
                {types.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-section">
              <div className="filter-label">Отдел ГИБДД</div>
              <select
                className="filter-select"
                value={filterDept}
                onChange={(e) => setFilterDept(e.target.value)}
              >
                <option value="">Все отделы</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="list-panel">
          {loading ? (
            <div className="loader">
              <div className="spinner" />
              Загрузка...
            </div>
          ) : filtered.length === 0 ? (
            <div className="empty">
              <div className="empty-icon">📄</div>
              <p>Актов не найдено</p>
            </div>
          ) : (
            filtered.map((a) => (
              <div className="list-item" key={a.id}>
                <div className="list-item-id">№ {a.id}</div>
                <div className="list-item-main">
                  {a.place.length > 30 ? a.place.slice(0, 30) + "..." : a.place}
                </div>
                <div className="list-item-sub">{a.department.name}</div>
                <div className="list-item-sub">
                  {new Date(a.date).toLocaleString("ru", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
                <div className="list-item-actions">
                  <button
                    className="btn btn-icon"
                    onClick={() => {
                      setEditAct(a);
                      setShowModal(true);
                    }}
                  >
                    <IconEdit />
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => setConfirmId(a.id)}
                  >
                    <IconTrash />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showModal && (
        <ActModal
          act={editAct}
          types={types}
          reasons={reasons}
          departments={departments}
          drivers={drivers}
          cars={cars}
          onClose={() => setShowModal(false)}
          onSaved={() => {
            setShowModal(false);
            load();
            setToast({
              msg: editAct ? "Акт обновлён" : "Акт создан",
              type: "success",
            });
          }}
          onError={(msg) => setToast({ msg, type: "error" })}
        />
      )}
      {confirmId !== null && (
        <Confirm
          msg="Удалить этот акт? Это действие необратимо."
          onConfirm={() => handleDelete(confirmId!)}
          onCancel={() => setConfirmId(null)}
        />
      )}
      {toast && (
        <Toast
          msg={toast.msg}
          type={toast.type}
          onDone={() => setToast(null)}
        />
      )}
    </div>
  );
}

function ActModal({
  act,
  types,
  reasons,
  departments,
  drivers,
  cars,
  onClose,
  onSaved,
  onError,
}: {
  act: Act | null;
  types: ActType[];
  reasons: ActReason[];
  departments: Department[];
  drivers: Driver[];
  cars: Car[];
  onClose: () => void;
  onSaved: () => void;
  onError: (m: string) => void;
}) {
  const [departmentId, setDepartmentId] = useState(
    act?.department.id.toString() || departments[0]?.id.toString() || "",
  );
  const [place, setPlace] = useState(act?.place || "");
  const [victims, setVictims] = useState(act?.victims?.toString() || "0");
  const [typeId, setTypeId] = useState(
    act?.accident_type.id.toString() || types[0]?.id.toString() || "",
  );
  const [reasonId, setReasonId] = useState(
    act?.accident_reason.id.toString() || reasons[0]?.id.toString() || "",
  );
  const [date, setDate] = useState(
    act ? act.date.slice(0, 16) : new Date().toISOString().slice(0, 16),
  );
  const [participants, setParticipants] = useState<
    { driver_id: string; car_id: string }[]
  >(
    act?.participants.map((p) => ({
      driver_id: p.driver.id.toString(),
      car_id: p.car.id.toString(),
    })) || [{ driver_id: "", car_id: "" }],
  );
  const [loading, setLoading] = useState(false);

  async function submit() {
    if (!place || !departmentId || !typeId || !reasonId)
      return onError("Заполните все обязательные поля");
    setLoading(true);
    try {
      const body = {
        department_id: parseInt(departmentId),
        place,
        victims: parseInt(victims) || 0,
        accident_type_id: parseInt(typeId),
        accident_reason_id: parseInt(reasonId),
        date: new Date(date).toISOString(),
      };
      let actId: number;
      if (act) {
        await apiFetch(`/api/acts/${act.id}`, {
          method: "PUT",
          body: JSON.stringify(body),
        });
        actId = act.id;
      } else {
        const created = await apiFetch<{ id: number }>("/api/acts/", {
          method: "POST",
          body: JSON.stringify(body),
        });
        actId = created.id;
        for (const p of participants) {
          if (p.driver_id && p.car_id) {
            await apiFetch("/api/participants/", {
              method: "POST",
              body: JSON.stringify({
                act_id: actId,
                driver_id: parseInt(p.driver_id),
                car_id: parseInt(p.car_id),
              }),
            });
          }
        }
      }
      onSaved();
    } catch (e: any) {
      onError(e.message);
    }
    setLoading(false);
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            {act ? "Редактировать акт" : "Новый акт"}
          </div>
          <button
            className="btn btn-ghost"
            style={{ padding: "4px" }}
            onClick={onClose}
          >
            <IconClose />
          </button>
        </div>

        <div className="form-group">
          <label className="form-label">Место ДТП *</label>
          <input
            className="form-input"
            value={place}
            onChange={(e) => setPlace(e.target.value)}
            placeholder="Укажите место аварии"
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Пострадавших</label>
            <input
              className="form-input"
              type="number"
              min="0"
              value={victims}
              onChange={(e) => setVictims(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Дата и время *</label>
            <input
              className="form-input"
              type="datetime-local"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
        </div>
        <div className="form-group">
          <label className="form-label">Отдел ГИБДД *</label>
          <select
            className="form-input"
            value={departmentId}
            onChange={(e) => setDepartmentId(e.target.value)}
          >
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Вид ДТП *</label>
            <select
              className="form-input"
              value={typeId}
              onChange={(e) => setTypeId(e.target.value)}
            >
              {types.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Причина ДТП *</label>
            <select
              className="form-input"
              value={reasonId}
              onChange={(e) => setReasonId(e.target.value)}
            >
              {reasons.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {!act && (
          <>
            <hr className="divider" />
            <div className="form-label" style={{ marginBottom: 12 }}>
              УЧАСТНИКИ ДТП
            </div>
            {participants.map((p, i) => (
              <div className="participant-row" key={i}>
                <select
                  className="filter-select"
                  style={{ flex: 1 }}
                  value={p.driver_id}
                  onChange={(e) => {
                    const np = [...participants];
                    np[i].driver_id = e.target.value;
                    setParticipants(np);
                  }}
                >
                  <option value="">Водитель...</option>
                  {drivers.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.full_name}
                    </option>
                  ))}
                </select>
                <select
                  className="filter-select"
                  style={{ flex: 1 }}
                  value={p.car_id}
                  onChange={(e) => {
                    const np = [...participants];
                    np[i].car_id = e.target.value;
                    setParticipants(np);
                  }}
                >
                  <option value="">Автомобиль...</option>
                  {cars.map((c) => (
                    <option key={c.id} value={c.id}>
                      [{c.number_plate}] {c.mark}
                    </option>
                  ))}
                </select>
                {participants.length > 1 && (
                  <button
                    className="btn btn-danger"
                    onClick={() =>
                      setParticipants(participants.filter((_, j) => j !== i))
                    }
                    style={{ padding: "6px" }}
                  >
                    <IconTrash />
                  </button>
                )}
              </div>
            ))}
            <button
              className="btn btn-outline"
              style={{ marginTop: 8, fontSize: 13 }}
              onClick={() =>
                setParticipants([
                  ...participants,
                  { driver_id: "", car_id: "" },
                ])
              }
            >
              <IconPlus /> Добавить участника
            </button>
          </>
        )}

        <div className="modal-actions">
          <button className="btn btn-outline" onClick={onClose}>
            Отмена
          </button>
          <button
            className="btn btn-primary"
            onClick={submit}
            disabled={loading}
          >
            {loading ? "Сохранение..." : "Сохранить"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Drivers Page ─────────────────────────────────────────────────────────────
function DriversPage() {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editDriver, setEditDriver] = useState<Driver | null>(null);
  const [confirmId, setConfirmId] = useState<number | null>(null);
  const [toast, setToast] = useState<{
    msg: string;
    type: "success" | "error";
  } | null>(null);
  const [search, setSearch] = useState("");
  const [filterDate, setFilterDate] = useState("");
  const [filterPlace, setFilterPlace] = useState("");
  const [repeatOnly, setRepeatOnly] = useState(false);
  const [pedestrianOnly, setPedestrianOnly] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      let data: Driver[];
      if (repeatOnly)
        data = await apiFetch<Driver[]>("/api/analytics/repeat-offenders");
      else if (pedestrianOnly)
        data = await apiFetch<Driver[]>("/api/analytics/pedestrian-accidents");
      else if (filterDate)
        data = await apiFetch<Driver[]>(
          `/api/analytics/drivers-by-date?target_date=${filterDate}`,
        );
      else if (filterPlace)
        data = await apiFetch<Driver[]>(
          `/api/analytics/drivers-by-place?place=${encodeURIComponent(filterPlace)}`,
        );
      else data = await apiFetch<Driver[]>("/api/drivers/");
      setDrivers(data);
    } catch {}
    setLoading(false);
  }, [repeatOnly, pedestrianOnly, filterDate, filterPlace]);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = drivers.filter(
    (d) =>
      !search ||
      d.full_name.toLowerCase().includes(search.toLowerCase()) ||
      d.driver_license.includes(search),
  );

  async function handleDelete(id: number) {
    try {
      await apiFetch(`/api/drivers/${id}`, { method: "DELETE" });
      setToast({ msg: "Водитель удалён", type: "success" });
      load();
    } catch (e: any) {
      setToast({ msg: e.message, type: "error" });
    }
    setConfirmId(null);
  }

  return (
    <div className="page">
      <h1 className="page-title">Водители</h1>
      <div className="content-layout">
        <div className="filters-panel">
          <div className="card filter-card">
            <div className="section-add-btn">
              <button
                className="btn btn-primary"
                style={{ width: "100%", justifyContent: "center" }}
                onClick={() => {
                  setEditDriver(null);
                  setShowModal(true);
                }}
              >
                <IconPlus /> Добавить
              </button>
            </div>
            <div className="filter-section">
              <div className="filter-label">Поиск</div>
              <input
                className="filter-input"
                placeholder="ФИО или номер ВУ..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="filter-section">
              <div className="filter-label">Дата ДТП</div>
              <input
                type="date"
                className="filter-input"
                value={filterDate}
                onChange={(e) => {
                  setFilterDate(e.target.value);
                  setRepeatOnly(false);
                  setPedestrianOnly(false);
                }}
              />
            </div>
            <div className="filter-section">
              <div className="filter-label">Место</div>
              <input
                className="filter-input"
                value={filterPlace}
                onChange={(e) => {
                  setFilterPlace(e.target.value);
                  setRepeatOnly(false);
                  setPedestrianOnly(false);
                }}
              />
            </div>
            <div className="filter-section">
              <div className="filter-checkbox-row">
                <input
                  type="checkbox"
                  id="repeat"
                  checked={repeatOnly}
                  onChange={(e) => {
                    setRepeatOnly(e.target.checked);
                    if (e.target.checked) setPedestrianOnly(false);
                  }}
                />
                <label htmlFor="repeat">Повторные ДТП</label>
              </div>
              <div className="filter-checkbox-row">
                <input
                  type="checkbox"
                  id="ped"
                  checked={pedestrianOnly}
                  onChange={(e) => {
                    setPedestrianOnly(e.target.checked);
                    if (e.target.checked) setRepeatOnly(false);
                  }}
                />
                <label htmlFor="ped">Наезд на пешехода</label>
              </div>
            </div>
          </div>
        </div>

        <div className="list-panel">
          {loading ? (
            <div className="loader">
              <div className="spinner" />
              Загрузка...
            </div>
          ) : filtered.length === 0 ? (
            <div className="empty">
              <div className="empty-icon">👤</div>
              <p>Водителей не найдено</p>
            </div>
          ) : (
            filtered.map((d) => (
              <div className="list-item" key={d.id}>
                <div
                  className="list-item-main"
                  style={{ fontWeight: 700, fontSize: 17 }}
                >
                  {d.full_name}
                </div>
                <div className="list-item-sub">{d.driver_license}</div>
                <div className="list-item-sub">
                  Стаж вождения: {d.driver_exp}{" "}
                  {d.driver_exp === 1
                    ? "год"
                    : d.driver_exp < 5
                      ? "года"
                      : "лет"}
                </div>
                <div className="list-item-actions">
                  <button
                    className="btn btn-icon"
                    onClick={() => {
                      setEditDriver(d);
                      setShowModal(true);
                    }}
                  >
                    <IconEdit />
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => setConfirmId(d.id)}
                  >
                    <IconTrash />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showModal && (
        <DriverModal
          driver={editDriver}
          onClose={() => setShowModal(false)}
          onSaved={() => {
            setShowModal(false);
            load();
            setToast({
              msg: editDriver ? "Данные обновлены" : "Водитель добавлен",
              type: "success",
            });
          }}
          onError={(msg) => setToast({ msg, type: "error" })}
        />
      )}
      {confirmId !== null && (
        <Confirm
          msg="Удалить водителя? Это действие необратимо."
          onConfirm={() => handleDelete(confirmId!)}
          onCancel={() => setConfirmId(null)}
        />
      )}
      {toast && (
        <Toast
          msg={toast.msg}
          type={toast.type}
          onDone={() => setToast(null)}
        />
      )}
    </div>
  );
}

function DriverModal({
  driver,
  onClose,
  onSaved,
  onError,
}: {
  driver: Driver | null;
  onClose: () => void;
  onSaved: () => void;
  onError: (m: string) => void;
}) {
  const [fullName, setFullName] = useState(driver?.full_name || "");
  const [exp, setExp] = useState(driver?.driver_exp?.toString() || "");
  const [license, setLicense] = useState(driver?.driver_license || "");
  const [loading, setLoading] = useState(false);

  async function submit() {
    if (!fullName || !license) return onError("Заполните все поля");
    setLoading(true);
    try {
      const body = {
        full_name: fullName,
        driver_exp: parseInt(exp) || 0,
        driver_license: license,
      };
      if (driver) {
        await apiFetch(`/api/drivers/${driver.id}`, {
          method: "PUT",
          body: JSON.stringify(body),
        });
      } else {
        await apiFetch("/api/drivers/", {
          method: "POST",
          body: JSON.stringify(body),
        });
      }
      onSaved();
    } catch (e: any) {
      onError(e.message);
    }
    setLoading(false);
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal"
        style={{ maxWidth: 420 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div className="modal-title">
            {driver ? "Редактировать водителя" : "Новый водитель"}
          </div>
          <button
            className="btn btn-ghost"
            style={{ padding: 4 }}
            onClick={onClose}
          >
            <IconClose />
          </button>
        </div>
        <div className="form-group">
          <label className="form-label">ФИО *</label>
          <input
            className="form-input"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Иванов Иван Иванович"
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Стаж (лет)</label>
            <input
              className="form-input"
              type="number"
              min="0"
              value={exp}
              onChange={(e) => setExp(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Номер ВУ *</label>
            <input
              className="form-input"
              value={license}
              onChange={(e) => setLicense(e.target.value)}
              placeholder="77 АВ 123456"
            />
          </div>
        </div>
        <div className="modal-actions">
          <button className="btn btn-outline" onClick={onClose}>
            Отмена
          </button>
          <button
            className="btn btn-primary"
            onClick={submit}
            disabled={loading}
          >
            {loading ? "Сохранение..." : "Сохранить"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Cars Page ────────────────────────────────────────────────────────────────
function CarsPage() {
  const [cars, setCars] = useState<Car[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editCar, setEditCar] = useState<Car | null>(null);
  const [confirmId, setConfirmId] = useState<number | null>(null);
  const [toast, setToast] = useState<{
    msg: string;
    type: "success" | "error";
  } | null>(null);
  const [firms, setFirms] = useState<Firm[]>([]);
  const [bodies, setBodies] = useState<Body[]>([]);
  const [search, setSearch] = useState("");
  const [filterFirm, setFilterFirm] = useState("");
  const [filterBody, setFilterBody] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [c, f, b] = await Promise.all([
        apiFetch<Car[]>("/api/cars/"),
        apiFetch<Firm[]>("/api/additional/firms/"),
        apiFetch<Body[]>("/api/additional/bodies/"),
      ]);
      setCars(c);
      setFirms(f);
      setBodies(b);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = cars.filter((c) => {
    if (
      search &&
      !c.number_plate.includes(search.toUpperCase()) &&
      !c.mark.toLowerCase().includes(search.toLowerCase())
    )
      return false;
    if (filterFirm && c.firm_id?.toString() !== filterFirm) return false;
    if (filterBody && c.body_type_id?.toString() !== filterBody) return false;
    return true;
  });

  async function handleDelete(id: number) {
    try {
      await apiFetch(`/api/cars/${id}`, { method: "DELETE" });
      setToast({ msg: "Автомобиль удалён", type: "success" });
      load();
    } catch (e: any) {
      setToast({ msg: e.message, type: "error" });
    }
    setConfirmId(null);
  }

  return (
    <div className="page">
      <h1 className="page-title">Автомобили</h1>
      <div className="content-layout">
        <div className="filters-panel">
          <div className="card filter-card">
            <div className="section-add-btn">
              <button
                className="btn btn-primary"
                style={{ width: "100%", justifyContent: "center" }}
                onClick={() => {
                  setEditCar(null);
                  setShowModal(true);
                }}
              >
                <IconPlus /> Добавить
              </button>
            </div>
            <div className="filter-section">
              <div className="filter-label">Поиск</div>
              <input
                className="filter-input"
                placeholder="Номер..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="filter-section">
              <div className="filter-label">Фирма</div>
              <select
                className="filter-select"
                value={filterFirm}
                onChange={(e) => setFilterFirm(e.target.value)}
              >
                <option value="">Все</option>
                {firms.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-section">
              <div className="filter-label">Тип кузова</div>
              <select
                className="filter-select"
                value={filterBody}
                onChange={(e) => setFilterBody(e.target.value)}
              >
                <option value="">Все</option>
                {bodies.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="list-panel">
          {loading ? (
            <div className="loader">
              <div className="spinner" />
              Загрузка...
            </div>
          ) : filtered.length === 0 ? (
            <div className="empty">
              <div className="empty-icon">🚗</div>
              <p>Автомобилей не найдено</p>
            </div>
          ) : (
            filtered.map((c) => {
              const firm = firms.find((f) => f.id === c.firm_id);
              const body = bodies.find((b) => b.id === c.body_type_id);
              return (
                <div className="list-item" key={c.id}>
                  <div className="plate-badge">[ {c.number_plate} ]</div>
                  <div className="list-item-main">{c.mark}</div>
                  {firm && <div className="list-item-sub">{firm.name}</div>}
                  {body && <div className="list-item-sub">{body.name}</div>}
                  <div className="list-item-actions">
                    <button
                      className="btn btn-icon"
                      onClick={() => {
                        setEditCar(c);
                        setShowModal(true);
                      }}
                    >
                      <IconEdit />
                    </button>
                    <button
                      className="btn btn-danger"
                      onClick={() => setConfirmId(c.id)}
                    >
                      <IconTrash />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {showModal && (
        <CarModal
          car={editCar}
          firms={firms}
          bodies={bodies}
          onClose={() => setShowModal(false)}
          onSaved={() => {
            setShowModal(false);
            load();
            setToast({
              msg: editCar ? "Данные обновлены" : "Автомобиль добавлен",
              type: "success",
            });
          }}
          onError={(msg) => setToast({ msg, type: "error" })}
        />
      )}
      {confirmId !== null && (
        <Confirm
          msg="Удалить автомобиль?"
          onConfirm={() => handleDelete(confirmId!)}
          onCancel={() => setConfirmId(null)}
        />
      )}
      {toast && (
        <Toast
          msg={toast.msg}
          type={toast.type}
          onDone={() => setToast(null)}
        />
      )}
    </div>
  );
}

function CarModal({
  car,
  firms,
  bodies,
  onClose,
  onSaved,
  onError,
}: {
  car: Car | null;
  firms: Firm[];
  bodies: Body[];
  onClose: () => void;
  onSaved: () => void;
  onError: (m: string) => void;
}) {
  const [mark, setMark] = useState(car?.mark || "");
  const [plate, setPlate] = useState(car?.number_plate || "");
  const [firmId, setFirmId] = useState(car?.firm_id?.toString() || "");
  const [bodyId, setBodyId] = useState(car?.body_type_id?.toString() || "");
  const [loading, setLoading] = useState(false);

  async function submit() {
    if (!mark || !plate) return onError("Заполните марку и гос. номер");
    setLoading(true);
    try {
      const body = {
        mark,
        number_plate: plate.toUpperCase(),
        firm_id: firmId ? parseInt(firmId) : null,
        body_type_id: bodyId ? parseInt(bodyId) : null,
      };
      if (car) {
        await apiFetch(`/api/cars/${car.id}`, {
          method: "PUT",
          body: JSON.stringify(body),
        });
      } else {
        await apiFetch("/api/cars/", {
          method: "POST",
          body: JSON.stringify(body),
        });
      }
      onSaved();
    } catch (e: any) {
      onError(e.message);
    }
    setLoading(false);
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal"
        style={{ maxWidth: 420 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div className="modal-title">
            {car ? "Редактировать автомобиль" : "Новый автомобиль"}
          </div>
          <button
            className="btn btn-ghost"
            style={{ padding: 4 }}
            onClick={onClose}
          >
            <IconClose />
          </button>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Марка *</label>
            <input
              className="form-input"
              value={mark}
              onChange={(e) => setMark(e.target.value)}
              placeholder="Lada Vesta"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Гос. номер *</label>
            <input
              className="form-input"
              value={plate}
              onChange={(e) => setPlate(e.target.value)}
              placeholder="А 123 АА 77"
              style={{ fontFamily: "monospace" }}
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Фирма</label>
            <select
              className="form-input"
              value={firmId}
              onChange={(e) => setFirmId(e.target.value)}
            >
              <option value="">Не указана</option>
              {firms.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Тип кузова</label>
            <select
              className="form-input"
              value={bodyId}
              onChange={(e) => setBodyId(e.target.value)}
            >
              <option value="">Не указан</option>
              {bodies.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="modal-actions">
          <button className="btn btn-outline" onClick={onClose}>
            Отмена
          </button>
          <button
            className="btn btn-primary"
            onClick={submit}
            disabled={loading}
          >
            {loading ? "Сохранение..." : "Сохранить"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── App root ─────────────────────────────────────────────────────────────────
export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem("token"));
  const [page, setPage] = useState<Page>("dashboard");
  const [searchQuery, setSearchQuery] = useState("");

  const userDisplay = (() => {
    const token = localStorage.getItem("token");
    if (!token)
      return { name: "Пользователь", role: "Инспектор", initials: "П" };
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const name = payload.sub || "Инспектор";
      return { name, role: "Отдел", initials: name[0]?.toUpperCase() || "И" };
    } catch {
      return { name: "Инспектор", role: "Отдел", initials: "И" };
    }
  })();

  function logout() {
    localStorage.removeItem("token");
    setAuthed(false);
  }

  if (!authed)
    return (
      <>
        <LoginPage onLogin={() => setAuthed(true)} />
      </>
    );

  return (
    <>
      <div className="layout">
        <Sidebar page={page} setPage={setPage} onLogout={logout} />
        <div className="main">
          <header className="topbar">
            <div className="search-box">
              <IconSearch />
              <input
                placeholder="Поиск"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div style={{ flex: 1 }} />
            <div className="user-badge">
              <div className="user-info">
                <div className="user-name">
                  {userDisplay.name.length > 20
                    ? userDisplay.name.slice(0, 20) + "..."
                    : userDisplay.name}
                </div>
                <div className="user-role">{userDisplay.role}</div>
              </div>
              <div className="user-avatar">{userDisplay.initials}</div>
            </div>
          </header>

          {page === "dashboard" && <DashboardPage />}
          {page === "acts" && <ActsPage />}
          {page === "drivers" && <DriversPage />}
          {page === "cars" && <CarsPage />}
        </div>
      </div>
    </>
  );
}
