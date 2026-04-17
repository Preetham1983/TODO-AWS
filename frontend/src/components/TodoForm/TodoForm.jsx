import React, { useState } from "react";
import "./TodoForm.css";

/**
 * TodoForm – Input form for creating new TODOs.
 */
function TodoForm({ onSubmit }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [expanded, setExpanded] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    onSubmit({ title: title.trim(), description: description.trim(), priority });
    setTitle("");
    setDescription("");
    setPriority("medium");
    setExpanded(false);
  };

  return (
    <form className="todo-form" onSubmit={handleSubmit}>
      <div className="todo-form__header">
        <h3>Create a task</h3>
        <p>Give it a clear title. Add details and priority if needed.</p>
      </div>

      <div className="todo-form__row">
        <input
          className="todo-form__input"
          type="text"
          placeholder="What do you need to get done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onFocus={() => setExpanded(true)}
          maxLength={200}
          required
        />
        <button
          className="todo-form__toggle"
          type="button"
          onClick={() => setExpanded((prev) => !prev)}
          aria-expanded={expanded}
        >
          {expanded ? "Hide details" : "More details"}
        </button>
        <button
          className="todo-form__submit"
          type="submit"
          disabled={!title.trim()}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Add
        </button>
      </div>

      {expanded && (
        <div className="todo-form__details">
          <textarea
            className="todo-form__textarea"
            placeholder="Add a description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            maxLength={2000}
          />
          <div className="todo-form__priority">
            <span className="todo-form__label">Priority:</span>
            {["low", "medium", "high"].map((p) => (
              <button
                key={p}
                type="button"
                className={`todo-form__priority-btn todo-form__priority-btn--${p} ${
                  priority === p ? "todo-form__priority-btn--active" : ""
                }`}
                onClick={() => setPriority(p)}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      )}
    </form>
  );
}

export default TodoForm;
