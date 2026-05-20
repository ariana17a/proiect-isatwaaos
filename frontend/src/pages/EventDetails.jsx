import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { API_BASE_URL, getEventDetails } from "../api";

function EventDetails() {
  const { id } = useParams();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadDetails() {
      setLoading(true);
      setError("");
      try {
        const data = await getEventDetails(id);
        if (isMounted) {
          setEvent(data);
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

    loadDetails();
    return () => {
      isMounted = false;
    };
  }, [id]);

  if (loading) {
    return <p className="status">Se incarca detaliile...</p>;
  }

  if (error) {
    return <p className="status error">{error}</p>;
  }

  if (!event) {
    return <p className="status">Evenimentul nu a fost gasit.</p>;
  }

  const icsUrl = `${API_BASE_URL}/events/${event.id}/export-ics`;

  return (
    <section className="glass-card details-card">
      <h2>{event.title}</h2>
      <p>{event.description || "Fara descriere disponibila."}</p>
      <div className="details-grid">
        <span><strong>Inceput:</strong> {new Date(event.start_datetime).toLocaleString()}</span>
        <span><strong>Final:</strong> {new Date(event.end_datetime).toLocaleString()}</span>
        <span><strong>Locatie:</strong> {event.location}</span>
        <span><strong>Categorie:</strong> {event.category}</span>
        <span><strong>Organizator:</strong> {event.organizer}</span>
        <span><strong>Tip participare:</strong> {event.participation_type}</span>
      </div>

      <div className="actions-row">
        <a className="glossy-button" href={icsUrl} target="_blank" rel="noreferrer">
          Exporta .ics
        </a>
        {event.registration_link && (
          <a className="ghost-button" href={event.registration_link} target="_blank" rel="noreferrer">
            Link inscriere
          </a>
        )}
      </div>
    </section>
  );
}

export default EventDetails;
