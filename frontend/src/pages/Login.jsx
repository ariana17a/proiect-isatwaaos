import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { getCurrentUser, login, saveToken } from "../api";

function Login({ onAuthChanged }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await login(form.email, form.password);
      saveToken(data.access_token);

      const me = await getCurrentUser(data.access_token);
      onAuthChanged(me);

      if (me.role === "organizer" || me.role === "admin") {
        navigate("/organizer", { replace: true });
      } else {
        navigate("/events", { replace: true });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="glass-card form-card auth-card">
      <h2>Login</h2>
      <form onSubmit={handleSubmit} className="form-grid">
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Parola"
          value={form.password}
          onChange={handleChange}
          required
        />
        <button className="glossy-button" type="submit" disabled={loading}>
          {loading ? "Se autentifica..." : "Login"}
        </button>
      </form>
      <p className="auth-switch">
        Nu ai cont? <Link to="/register">Create Account</Link>
      </p>
      {error && <p className="status error">{error}</p>}
    </section>
  );
}

export default Login;
