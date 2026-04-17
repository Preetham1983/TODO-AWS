import React, { useState, useEffect, useCallback } from "react";
import { NotificationApiService } from "../../services/NotificationApiService";
import "./NotificationPanel.css";

/**
 * NotificationPanel – Slide-in panel showing sent email notifications.
 */
function NotificationPanel({ onClose }) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true);
      const data = await NotificationApiService.getAll();
      setNotifications(data.items || []);
    } catch (err) {
      console.error("Failed to fetch notifications", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const statusBadge = (status) => {
    const map = {
      sent: "notification-panel__badge--sent",
      failed: "notification-panel__badge--failed",
      queued: "notification-panel__badge--queued",
    };
    return `notification-panel__badge ${map[status] || ""}`;
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="notification-panel__overlay" onClick={onClose}>
      <aside
        className="notification-panel"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="notification-panel__header">
          <h2>Activity & Notifications</h2>
          <button className="notification-panel__close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="notification-panel__body">
          {loading ? (
            <p className="notification-panel__empty">Loading…</p>
          ) : notifications.length === 0 ? (
            <p className="notification-panel__empty">No notifications yet. Updates will appear here.</p>
          ) : (
            <ul className="notification-panel__list">
              {notifications.map((n) => (
                <li key={n.id} className="notification-panel__item">
                  <div className="notification-panel__item-header">
                    <span className={statusBadge(n.status)}>{n.status}</span>
                    <span className="notification-panel__date">
                      {formatDate(n.created_at)}
                    </span>
                  </div>
                  <h4 className="notification-panel__subject">{n.subject}</h4>
                  <p className="notification-panel__recipient">
                    To: {n.recipient_email}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>
    </div>
  );
}

export default NotificationPanel;
