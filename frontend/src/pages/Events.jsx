import { useEffect, useState } from "react";

import EventCard from "../components/EventCard";
import { getPublicEvents } from "../api";

const initialFilters = {
  category: "",
  location: "",
  organizer: "",
};

function Events() {
  const [filters, setFilters] = useState(initialFilters);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadEvents() {
      setLoading(true);
      setError("");
      try {
        const data = await getPublicEvents(filters);
        if (isMounted) {
          setEvents(data);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadEvents();
    return () => {
      isMounted = false;
    };
  }, [filters]);

  function handleFilterChange(event) {
    const { name, value } = event.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  }

  function clearFilters() {
    setFilters(initialFilters);
  }

  return (
    <section>
      <div className="glass-card filter-panel">
        <h2>Evenimente publice</h2>
        <div className="filters">
          <input
            name="category"
            value={filters.category}
            onChange={handleFilterChange}
            placeholder="Filtreaza dupa categorie"
          />
          <input
            name="location"
            value={filters.location}
            onChange={handleFilterChange}
            placeholder="Filtreaza dupa locatie"
          />
          <input
            name="organizer"
            value={filters.organizer}
            onChange={handleFilterChange}
            placeholder="Filtreaza dupa organizator"
          />
          <button type="button" className="ghost-button" onClick={clearFilters}>
            Reseteaza filtre
          </button>
        </div>
      </div>

      {loading && <p className="status">Se incarca evenimentele...</p>}
      {error && <p className="status error">{error}</p>}
      {!loading && !error && events.length === 0 && (
        <p className="status">Nu exista evenimente pentru filtrele selectate.</p>
      )}

      <div className="cards-grid">
        {events.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </section>
  );
}

export default Events;
