import React from "react";
import TodoItem from "../TodoItem/TodoItem";
import "./TodoList.css";

/**
 * TodoList – Renders the collection of TODO items.
 */
function TodoList({ todos, loading, onUpdate, onDelete }) {
  if (loading) {
    return (
      <div className="todo-list__empty">
        <div className="todo-list__spinner" />
        <p>Loading your tasks…</p>
      </div>
    );
  }

  if (todos.length === 0) {
    return (
      <div className="todo-list__empty">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="todo-list__empty-icon">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <line x1="9" y1="9" x2="15" y2="15" />
          <line x1="15" y1="9" x2="9" y2="15" />
        </svg>
        <p>No tasks yet</p>
        <span>Create your first task above</span>
      </div>
    );
  }

  // Group by status
  const pending = todos.filter((t) => t.status === "pending");
  const inProgress = todos.filter((t) => t.status === "in_progress");
  const completed = todos.filter((t) => t.status === "completed");

  return (
    <div className="todo-list">
      {inProgress.length > 0 && (
        <section className="todo-list__section">
          <h2 className="todo-list__heading todo-list__heading--progress">
            <span className="todo-list__dot todo-list__dot--progress" />
            In Progress ({inProgress.length})
          </h2>
          {inProgress.map((todo) => (
            <TodoItem key={todo.id} todo={todo} onUpdate={onUpdate} onDelete={onDelete} />
          ))}
        </section>
      )}

      {pending.length > 0 && (
        <section className="todo-list__section">
          <h2 className="todo-list__heading todo-list__heading--pending">
            <span className="todo-list__dot todo-list__dot--pending" />
            Pending ({pending.length})
          </h2>
          {pending.map((todo) => (
            <TodoItem key={todo.id} todo={todo} onUpdate={onUpdate} onDelete={onDelete} />
          ))}
        </section>
      )}

      {completed.length > 0 && (
        <section className="todo-list__section">
          <h2 className="todo-list__heading todo-list__heading--completed">
            <span className="todo-list__dot todo-list__dot--completed" />
            Completed ({completed.length})
          </h2>
          {completed.map((todo) => (
            <TodoItem key={todo.id} todo={todo} onUpdate={onUpdate} onDelete={onDelete} />
          ))}
        </section>
      )}
    </div>
  );
}

export default TodoList;
