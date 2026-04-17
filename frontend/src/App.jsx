import React, { useState, useEffect, useCallback, useMemo } from "react";
import Header from "./components/Header/Header";
import TodoForm from "./components/TodoForm/TodoForm";
import TodoList from "./components/TodoList/TodoList";
import NotificationPanel from "./components/NotificationPanel/NotificationPanel";
import { TodoApiService } from "./services/TodoApiService";
import { NotificationApiService } from "./services/NotificationApiService";
import "./App.css";

/**
 * App – Root component.
 * Composes the header, form, list and notification panel.
 */
function App() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  // ── Fetch all TODOs ─────────────────────────────────────────────────────

  const fetchTodos = useCallback(async () => {
    try {
      setLoading(true);
      const data = await TodoApiService.getAll();
      setTodos(data.items || []);
      setError(null);
    } catch (err) {
      setError("Failed to load todos. Is the backend running?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  // ── Handlers ────────────────────────────────────────────────────────────

  const handleCreate = async (payload) => {
    try {
      const created = await TodoApiService.create(payload);
      setTodos((prev) => [created, ...prev]);
      // Fire-and-forget: notification should never block CRUD
      NotificationApiService.send({
        recipient_email: "bandipreethamreddy16@gmail.com",
        subject: `New TODO: ${created.title}`,
        body_text: `You created a new task: "${created.title}"`,
        notification_type: "todo_created",
        todo_id: created.id,
      }).catch((err) => console.warn("Notification failed (non-blocking):", err));
    } catch (err) {
      setError("Failed to create todo");
      console.error(err);
    }
  };

  const handleUpdate = async (id, payload) => {
    try {
      const updated = await TodoApiService.update(id, payload);
      setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)));
      // Fire-and-forget: notification should never block CRUD
      if (payload.status === "completed") {
        NotificationApiService.send({
          recipient_email: "bandipreethamreddy16@gmail.com",
          subject: `TODO Completed: ${updated.title}`,
          body_text: `Great job! You completed "${updated.title}"`,
          notification_type: "todo_completed",
          todo_id: updated.id,
        }).catch((err) => console.warn("Notification failed (non-blocking):", err));
      }
    } catch (err) {
      setError("Failed to update todo");
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await TodoApiService.delete(id);
      setTodos((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      setError("Failed to delete todo");
      console.error(err);
    }
  };

  // ── Derived UI state ─────────────────────────────────────────────────────

  const counts = useMemo(() => {
    const pending = todos.filter((t) => t.status === "pending").length;
    const inProgress = todos.filter((t) => t.status === "in_progress").length;
    const completed = todos.filter((t) => t.status === "completed").length;
    return {
      total: todos.length,
      pending,
      inProgress,
      completed,
    };
  }, [todos]);

  const filteredTodos = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    return todos.filter((todo) => {
      const statusMatch =
        statusFilter === "all" ? true : todo.status === statusFilter;

      const textMatch =
        query.length === 0
          ? true
          : todo.title.toLowerCase().includes(query) ||
            todo.description.toLowerCase().includes(query);

      return statusMatch && textMatch;
    });
  }, [todos, searchTerm, statusFilter]);

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="app">
      <Header
        todoCount={todos.length}
        onToggleNotifications={() => setShowNotifications((s) => !s)}
      />

      <main className="app__main container">
        <section className="app__hero">
          <h2 className="app__hero-title">Your task hub, clear and simple</h2>
          <p className="app__hero-subtitle">
            Add tasks, change status, attach files, and track updates from one clean screen.
          </p>
          <div className="app__quick-help" aria-label="How to use">
            <span>1. Create a task</span>
            <span>2. Tap the status circle to move it forward</span>
            <span>3. Use filters to focus</span>
          </div>
        </section>

        {error && (
          <div className="app__error">
            <span>⚠️</span>
            <p>{error}</p>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <section className="app__stats" aria-label="Task summary">
          <div className="app__stat-card">
            <span className="app__stat-label">Total</span>
            <strong className="app__stat-value">{counts.total}</strong>
          </div>
          <div className="app__stat-card app__stat-card--pending">
            <span className="app__stat-label">Pending</span>
            <strong className="app__stat-value">{counts.pending}</strong>
          </div>
          <div className="app__stat-card app__stat-card--progress">
            <span className="app__stat-label">In Progress</span>
            <strong className="app__stat-value">{counts.inProgress}</strong>
          </div>
          <div className="app__stat-card app__stat-card--completed">
            <span className="app__stat-label">Completed</span>
            <strong className="app__stat-value">{counts.completed}</strong>
          </div>
        </section>

        <TodoForm onSubmit={handleCreate} />

        <section className="app__controls" aria-label="Todo filters">
          <input
            className="app__search"
            type="search"
            placeholder="Search tasks by title or description"
            aria-label="Search tasks"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <div className="app__filters" role="tablist" aria-label="Status filters">
            <button
              className={`app__filter-btn ${statusFilter === "all" ? "is-active" : ""}`}
              onClick={() => setStatusFilter("all")}
              type="button"
            >
              All ({counts.total})
            </button>
            <button
              className={`app__filter-btn ${statusFilter === "pending" ? "is-active" : ""}`}
              onClick={() => setStatusFilter("pending")}
              type="button"
            >
              Pending ({counts.pending})
            </button>
            <button
              className={`app__filter-btn ${statusFilter === "in_progress" ? "is-active" : ""}`}
              onClick={() => setStatusFilter("in_progress")}
              type="button"
            >
              In Progress ({counts.inProgress})
            </button>
            <button
              className={`app__filter-btn ${statusFilter === "completed" ? "is-active" : ""}`}
              onClick={() => setStatusFilter("completed")}
              type="button"
            >
              Completed ({counts.completed})
            </button>
          </div>
        </section>

        <TodoList
          todos={filteredTodos}
          loading={loading}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
        />
      </main>

      {showNotifications && (
        <NotificationPanel onClose={() => setShowNotifications(false)} />
      )}
    </div>
  );
}

export default App;
