import { useState } from "react";

import { createEvent, getToken } from "../api";

const defaultData = {
  title: "",
  description: "",
  start_datetime: "",
  end_datetime: "",
  location: "",
  category: "",
  participation_type: "onsite",
  organizer: "",
  registration_link: "",
  is_published: true,
};

function Organizer() {
  const [form, setForm] = useState(defaultData);
  const [message, setMessage] = useState("");
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
    setMessage("");

    try {
      const token = getToken();
      if (!token) {
        throw new Error("Nu exista token. Fa login mai intai.");
      }

      const payload = {
        ...form,
        start_datetime: new Date(form.start_datetime).toISOString(),
        end_datetime: new Date(form.end_datetime).toISOString(),
      };

      const created = await createEvent(payload, token);
      setMessage(`Eveniment creat cu succes (ID: ${created.id}).`);
      setForm(defaultData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="glass-card form-card">
      <h2>Organizer Panel</h2>
      <form onSubmit={handleSubmit} className="form-grid two-col">
        <input name="title" placeholder="Titlu" value={form.title} onChange={handleChange} required />
        <input name="organizer" placeholder="Organizator" value={form.organizer} onChange={handleChange} required />
        <textarea
          name="description"
          placeholder="Descriere"
          value={form.description}
          onChange={handleChange}
          rows={4}
        />
        <input name="category" placeholder="Categorie" value={form.category} onChange={handleChange} required />
        <input type="datetime-local" name="start_datetime" value={form.start_datetime} onChange={handleChange} required />
        <input type="datetime-local" name="end_datetime" value={form.end_datetime} onChange={handleChange} required />
        <input name="location" placeholder="Locatie" value={form.location} onChange={handleChange} required />
        <input
          name="registration_link"
          placeholder="Link inscriere"
          value={form.registration_link}
          onChange={handleChange}
        />
        <select name="participation_type" value={form.participation_type} onChange={handleChange}>
          <option value="onsite">Onsite</option>
          <option value="online">Online</option>
          <option value="hybrid">Hybrid</option>
        </select>
        <button className="glossy-button" type="submit" disabled={loading}>
          {loading ? "Se creeaza..." : "Creeaza eveniment"}
        </button>
      </form>
      {message && <p className="status success">{message}</p>}
      {error && <p className="status error">{error}</p>}
    </section>
  );
}

export default Organizer;
