import { Link } from "react-router-dom";

function Home() {
  return (
    <section className="hero glass-card">
      <p className="hero-kicker">Platforma universitara</p>
      <h1>Descopera evenimente, workshop-uri si oportunitati academice</h1>
      <p>
        University Events Platform centralizeaza activitatile din campus intr-o
        experienta moderna, clara si usor de urmarit pentru studenti,
        organizatori si administratie.
      </p>
      <Link className="glossy-button large" to="/events">
        Exploreaza evenimentele
      </Link>
    </section>
  );
}

export default Home;
