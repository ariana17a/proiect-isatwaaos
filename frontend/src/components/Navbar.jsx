import { NavLink } from "react-router-dom";

function Navbar({ currentUser, onLogout }) {
  const isAuthenticated = Boolean(currentUser);
  const canCreateEvents = currentUser?.role === "organizer" || currentUser?.role === "admin";

  return (
    <header className="glass-nav">
      <div className="brand-wrap">
        <img src="/siglausv.png" alt="Sigla USV" className="brand-logo" />
        <div className="brand">University Events Platform</div>
      </div>
      <nav className="nav-links">
        <NavLink to="/">Home</NavLink>
        <NavLink to="/events">Events</NavLink>
        {!isAuthenticated && <NavLink to="/login">Login</NavLink>}
        {!isAuthenticated && <NavLink to="/register">Register</NavLink>}
        {isAuthenticated && canCreateEvents && <NavLink to="/organizer">Organizer</NavLink>}
        {isAuthenticated && (
          <button type="button" className="nav-logout" onClick={onLogout}>
            Logout
          </button>
        )}
      </nav>
    </header>
  );
}

export default Navbar;
