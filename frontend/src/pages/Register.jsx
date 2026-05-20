import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { getCurrentUser, register as registerUser, saveToken } from "../api";

function Register({ onAuthChanged }) {
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
      const data = await registerUser({
        email: form.email,
        password: form.password,
        role: "student",
      });
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
      <h2>Create Account</h2>
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
          placeholder="Parola (minim 6 caractere)"
          value={form.password}
          onChange={handleChange}
          minLength={6}
          required
        />
        <button className="glossy-button" type="submit" disabled={loading}>
          {loading ? "Se creeaza contul..." : "Create Account"}
        </button>
      </form>
      <p className="auth-switch">
        Ai deja cont? <Link to="/login">Login</Link>
      </p>
      {error && <p className="status error">{error}</p>}
    </section>
  );
}

export default Register;
