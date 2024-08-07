# cosearch-api

Backend of CoSearch APP.

## Local

## Run app

Deploy and run the backend using Docker:

```bash
    docker compose up -d
```

```bash
    uvicorn app.main:app --reload
```

To kill the app, run

```bash
docker compose down
```

### Run tests

To run test locally, you must create a database and specify its name in the  `app/tests/conftest.py` file.

Up the docker with `docker compose up -d` and create the database using `Adminer`.

## URLs

Backend : [http://localhost:8000](http://localhost:8000)

Automatic Interactive Docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

Adminer: [http://localhost:8080](http://localhost:8080)
