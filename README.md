# Backoffice Service

The project can be run using Docker Compose, which will set up a MongoDB container and a Python application container:


---

# Install

git clone https://github.com/ClassConnect-2025C1/Classconnect-BackOffice-Service-API#

---

## Project Structure

```plaintext
src/app/
├── config/ # App configuration (env, settings)
├── db/ # Database connection (MongoDB client)
├── entities/ # Structure models used within the app
├── exceptions/ # Custom exceptions used within the application.
├── externals/ # Logic for making requests to other microservices.
├── models/ # Pydantic models (data layer)
├── routes/ # API endpoints (routers)
├── schemas/ # Request/response schemas
├── services/ # Business logic/services
├── main.py # App entrypoint
tests/ # Unit and integration tests
requirements/ # Dependency requirements (dev/prod)
docker-compose.yml # Docker Compose for local dev
Dockerfile # Dockerfile for production image
.env.example # Example environment variables
README.md # You are here
```

## Running the Application

### Locally

#### Requirements

- Python 3.8+
- MongoDB

All other dependencies can be installed using the requirements files, using the following command:

```bash
pip install -r requirements.txt
```

#### Command

To run the application locally, use the following command:

```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or with the arguments `--host` and `--port` set to your desired values.

### Using Docker

#### Requirements
- Docker
- Docker Compose

#### Build

To build the Docker image, use the following command:

```bash
docker-compose build
```

#### Run

To run the database, use the following command:

```bash
docker-compose up -d mongo
```

To run the application, use the following command:

```bash
docker-compose up -d api
```

#### Stop the Application

To stop the application, use the following command:

```bash
docker-compose down
```

## 📚 Documentación de la API

 - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
 - Production: [Backoffice docs](https://classconnect-backoffice-service-api.onrender.com/docs)