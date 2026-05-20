import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { clearToken, getCurrentUser, getToken } from "./api";
import Navbar from "./components/Navbar";
import AccessDenied from "./pages/AccessDenied";
import EventDetails from "./pages/EventDetails";
import Events from "./pages/Events";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Organizer from "./pages/Organizer";
import Register from "./pages/Register";

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [authResolved, setAuthResolved] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setAuthResolved(true);
      return;
    }

    getCurrentUser(token)
      .then((user) => setCurrentUser(user))
      .catch(() => {
        clearToken();
        setCurrentUser(null);
      })
      .finally(() => setAuthResolved(true));
  }, []);

  function handleAuthChanged(user) {
    setCurrentUser(user);
  }

  function handleLogout() {
    clearToken();
    setCurrentUser(null);
  }

  function resolveDefaultRoute() {
    if (!currentUser) {
      return "/events";
    }
    return currentUser.role === "organizer" || currentUser.role === "admin" ? "/organizer" : "/events";
  }

  function renderOrganizerRoute() {
    if (!authResolved) {
      return null;
    }

    if (!currentUser) {
      return <Navigate to="/login" replace />;
    }

    if (currentUser.role !== "organizer" && currentUser.role !== "admin") {
      return <Navigate to="/access-denied" replace />;
    }

    return <Organizer />;
  }

  function renderGuestOnlyRoute(element) {
    if (!authResolved) {
      return null;
    }

    if (currentUser) {
      return <Navigate to={resolveDefaultRoute()} replace />;
    }

    return element;
  }

  return (
    <div className="app-shell">
      <div className="bg-orb orb-left" />
      <div className="bg-orb orb-right" />
      <Navbar currentUser={currentUser} onLogout={handleLogout} />
      <main className="page-container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/events" element={<Events />} />
          <Route path="/events/:id" element={<EventDetails />} />
          <Route path="/access-denied" element={<AccessDenied />} />
          <Route
            path="/login"
            element={renderGuestOnlyRoute(<Login onAuthChanged={handleAuthChanged} />)}
          />
          <Route
            path="/register"
            element={renderGuestOnlyRoute(<Register onAuthChanged={handleAuthChanged} />)}
          />
          <Route path="/organizer" element={renderOrganizerRoute()} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
