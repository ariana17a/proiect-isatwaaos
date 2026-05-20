# University Events Management (USV) - Microservices MVP

Aplicația este refactorizată la arhitectură de tip microservicii, cu API Gateway ca punct unic de acces pentru frontend.

## Arhitectură implementată

- `api-gateway`: primește toate request-urile externe și le redirecționează către servicii interne.
- `auth-service`: autentificare JWT, management users, roluri (`student`, `organizer`, `admin`), placeholder OAuth Google.
- `events-service`: CRUD evenimente, filtrare, public events, event details, export ICS, QR code generation.
- `feedback-service`: feedback/rating 1-5, comentarii, statistici.
- `notifications-service`: MVP pentru notificări (endpoint de preview, pregătit pentru email reminders).
- `frontend`: React + Vite (design Frutiger Aqua), conectat la API Gateway.

## Structura proiectului

```text
.
├── api-gateway/
├── auth-service/
├── events-service/
├── feedback-service/
├── notifications-service/
├── frontend/
├── backend/                        # păstrat pentru referință/migrare
├── docker-compose.yml
└── README.md
```

## Rutare prin API Gateway

Toate request-urile frontend merg către `http://localhost:8000`:

- `/auth/*` și `/users/*` -> `auth-service`
- `/events/*` -> `events-service`
- `/feedback/*` -> `feedback-service`
- `/notifications/*` -> `notifications-service`

## Rulare Docker

1. Build și start:

```bash
docker compose up -d --build
```

2. Verificare servicii:

```bash
docker compose ps
```

3. Oprire:

```bash
docker compose down --remove-orphans
```

## URL-uri utile

- Frontend: `http://localhost:3000`
- API Gateway health: `http://localhost:8000/health`
- API docs (gateway): `http://localhost:8000/docs`
- Public events (prin gateway): `http://localhost:8000/events/public`

## Observații tehnice

- Serviciile backend sunt FastAPI + SQLAlchemy.
- Persistența este pe volum Docker (`core_data`) montat în serviciile care folosesc baza de date.
- JWT-ul este validat în servicii, păstrând comportamentul existent.
- `notifications-service` este MVP și poate fi extins cu trimitere email/queue.

## Validare realizată

Au fost testate cu succes după refactorizare:

- `GET /health` prin gateway -> `200`
- `GET /events/public` prin gateway -> `200`
- `POST /notifications/preview` prin gateway -> `200`
- Frontend `http://localhost:3000` -> `200`
