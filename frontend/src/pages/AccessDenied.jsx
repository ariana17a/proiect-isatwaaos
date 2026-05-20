import { Link } from "react-router-dom";

function AccessDenied() {
  return (
    <section className="glass-card form-card access-denied-card">
      <p className="hero-kicker">Restricted Area</p>
      <h2>Acces interzis pentru contul tau</h2>
      <p>
        Pagina Organizer este disponibila doar pentru rolurile <strong>organizer</strong> si <strong>admin</strong>.
      </p>
      <div className="actions-row">
        <Link className="glossy-button" to="/events">
          Vezi evenimente
        </Link>
        <Link className="ghost-button" to="/">
          Inapoi la Home
        </Link>
      </div>
    </section>
  );
}

export default AccessDenied;
