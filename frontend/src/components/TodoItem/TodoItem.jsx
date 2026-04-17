import React, { useState } from "react";
import AttachmentSection from "../AttachmentSection/AttachmentSection";
import "./TodoItem.css";

/**
 * TodoItem – Single task card with status toggle, edit & delete.
 */
function TodoItem({ todo, onUpdate, onDelete }) {
  const [showAttachments, setShowAttachments] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDescription, setEditDescription] = useState(todo.description || "");
  const [editPriority, setEditPriority] = useState(todo.priority || "medium");

  const priorityClass = `todo-item__priority--${todo.priority}`;
  const isCompleted = todo.status === "completed";
  const statusLabel = {
    pending: "Pending",
    in_progress: "In progress",
    completed: "Completed",
  }[todo.status] || todo.status;

  const cycleStatus = () => {
    const next = {
      pending: "in_progress",
      in_progress: "completed",
      completed: "pending",
    };
    onUpdate(todo.id, { status: next[todo.status] });
  };

  const handleSaveEdit = () => {
    if (!editTitle.trim()) {
      alert("Title cannot be empty");
      return;
    }
    onUpdate(todo.id, {
      title: editTitle,
      description: editDescription,
      priority: editPriority,
    });
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditTitle(todo.title);
    setEditDescription(todo.description || "");
    setEditPriority(todo.priority || "medium");
    setIsEditing(false);
  };

  const statusIcon = () => {
    if (todo.status === "completed")
      return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      );
    if (todo.status === "in_progress")
      return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
      );
    return <span className="todo-item__circle" />;
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <article className={`todo-item ${isCompleted ? "todo-item--completed" : ""} ${isEditing ? "todo-item--editing" : ""}`}>
      <div className="todo-item__main">
        <button
          className={`todo-item__status todo-item__status--${todo.status}`}
          onClick={cycleStatus}
          title={`Status: ${todo.status} (click to change)`}
          aria-label={`Change status for ${todo.title}`}
          disabled={isEditing}
        >
          {statusIcon()}
        </button>

        {!isEditing ? (
          <div className="todo-item__content">
            <h3 className="todo-item__title">{todo.title}</h3>
            {todo.description && (
              <p className="todo-item__description">{todo.description}</p>
            )}
            <div className="todo-item__meta">
              <span className={`todo-item__status-label todo-item__status-label--${todo.status}`}>
                {statusLabel}
              </span>
              <span className={`todo-item__priority ${priorityClass}`}>
                {todo.priority}
              </span>
              <span className="todo-item__date">{formatDate(todo.created_at)}</span>
              {todo.attachment_ids?.length > 0 && (
                <span className="todo-item__attachment-count">
                  📎 {todo.attachment_ids.length}
                </span>
              )}
            </div>
          </div>
        ) : (
          <div className="todo-item__edit-form">
            <input
              type="text"
              className="todo-item__edit-input"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              placeholder="Task title"
              autoFocus
            />
            <textarea
              className="todo-item__edit-textarea"
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              placeholder="Task description (optional)"
              rows="2"
            />
            <select
              className="todo-item__edit-select"
              value={editPriority}
              onChange={(e) => setEditPriority(e.target.value)}
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
          </div>
        )}

        <div className="todo-item__actions">
          {!isEditing && (
            <>
              <button
                className="todo-item__action-btn"
                onClick={() => setShowAttachments((s) => !s)}
                title="Attachments"
                aria-label={`Manage attachments for ${todo.title}`}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
                </svg>
                <span className="todo-item__action-text">Files</span>
              </button>
              <button
                className="todo-item__action-btn todo-item__action-btn--edit"
                onClick={() => setIsEditing(true)}
                title="Edit"
                aria-label={`Edit ${todo.title}`}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
                <span className="todo-item__action-text">Edit</span>
              </button>
              <button
                className="todo-item__action-btn todo-item__action-btn--danger"
                onClick={() => {
                  const shouldDelete = window.confirm(
                    `Delete task \"${todo.title}\"? This cannot be undone.`
                  );
                  if (shouldDelete) {
                    onDelete(todo.id);
                  }
                }}
                title="Delete"
                aria-label={`Delete ${todo.title}`}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                </svg>
                <span className="todo-item__action-text">Delete</span>
              </button>
            </>
          )}
          {isEditing && (
            <>
              <button
                className="todo-item__action-btn todo-item__action-btn--success"
                onClick={handleSaveEdit}
                title="Save"
                aria-label="Save changes"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span className="todo-item__action-text">Save</span>
              </button>
              <button
                className="todo-item__action-btn todo-item__action-btn--cancel"
                onClick={handleCancelEdit}
                title="Cancel"
                aria-label="Cancel editing"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
                <span className="todo-item__action-text">Cancel</span>
              </button>
            </>
          )}
        </div>
      </div>

      {showAttachments && (
        <AttachmentSection todoId={todo.id} />
      )}
    </article>
  );
}

export default TodoItem;
