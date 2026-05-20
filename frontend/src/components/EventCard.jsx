import { Link } from "react-router-dom";

function EventCard({ event }) {
  return (
    <article className="glass-card event-card">
      <h3>{event.title}</h3>
      <p className="event-description">{event.description || "Fara descriere."}</p>
      <div className="meta-grid">
        <span><strong>Locatie:</strong> {event.location}</span>
        <span><strong>Categorie:</strong> {event.category}</span>
        <span><strong>Organizator:</strong> {event.organizer}</span>
        <span><strong>Participare:</strong> {event.participation_type}</span>
      </div>
      <Link className="glossy-button" to={`/events/${event.id}`}>
        Vezi detalii
      </Link>
    </article>
  );
}

export default EventCard;
