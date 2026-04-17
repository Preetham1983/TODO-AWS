import React from "react";
import "./Header.css";

/**
 * Header – Top navigation bar with branding and notification toggle.
 */
function Header({ todoCount, onToggleNotifications }) {
  return (
    <header className="header">
      <div className="header__inner container">
        <div className="header__brand">
          <div className="header__logo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
            </svg>
          </div>
          <div>
            <h1 className="header__title">TODO</h1>
            <p className="header__subtitle">{todoCount} task{todoCount !== 1 ? "s" : ""}</p>
          </div>
        </div>

        <nav className="header__actions">
          <button
            className="header__btn"
            onClick={onToggleNotifications}
            title="Notifications"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 01-3.46 0" />
            </svg>
            <span>Activity</span>
          </button>
        </nav>
      </div>
    </header>
  );
}

export default Header;
