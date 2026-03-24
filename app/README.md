# Important info for Docker & FastAPI
## Starting & Stopping

### just like before with the timescaledb, this will also start fastapi
docker compose up -d

### stop everything
docker compose down

### restart just fastapi
docker compose restart fastapi

## Viewing Logs

docker compose logs -f fastapi

docker compose logs -f timescaledb

## Running Python Files

Any file in the volumes section of `docker-compose.yml` can be accessed.
If you want to access a file in a different folder, add it with the same schema as the other directories.

### example of running /database/example.py
docker exec lsu-fsae-fastapi python /database/example.py

### open an interactive Python shell
docker exec -it lsu-fsae-fastapi python

### open a full bash shell inside the container
docker exec -it lsu-fsae-fastapi bash

## Adding a New Package

1. Add it to `app/requirements.txt`:

2. Recreate the container:

`docker compose up --force-recreate fastapi`

If you just want to test a package before adding for everyone:

`docker exec lsu-fsae-fastapi pip install [package]`

## API Links

`http://localhost:8000` - API status
`http://localhost:8000/health` - DB connection
`http://localhost:8000/docs` - Interactive API docs

## VSCode Example 

**1. Install the Python extension in VSCode**

**2. Create a virtual environment:**
`cd app`
`python -m venv venv`

**3. Select the interpreter in VSCode:**
- Open Command Palette `Python: Select Interpreter`
- Pick the one inside `./app/venv`

**4. Install dependencies in the VSCode terminal:**
`source venv/bin/activate` OR `source venv\Scripts\activate`

`pip install -r requirements.txt`

**5. Start the database:**
`docker compose up -d timescaledb`

**6. Run FastAPI:**
`uvicorn main:app --reload`

## Adding New API Route example:
```
 simple GET route — no database
@app.get("/hello")
async def hello():
    return {"message": "hello from FSAE"}


# GET route with a URL parameter + database query
@app.get("/sensor/{sensor_id}")
async def get_sensor(sensor_id: str, request: Request):
    async with request.app.state.pool.connection() as conn:
        rows = await (await conn.execute(
            "SELECT time, value FROM telemetry WHERE sensor_id = %s ORDER BY time DESC LIMIT 100",
            (sensor_id,)
        )).fetchall()
    return [{"time": str(r[0]), "value": r[1]} for r in rows]


# POST route — write data to the database
@app.post("/sensor/{sensor_id}")
async def post_sensor(sensor_id: str, value: float, request: Request):
    async with request.app.state.pool.connection() as conn:
        await conn.execute(
            "INSERT INTO telemetry (time, sensor_id, value) VALUES (NOW(), %s, %s)",
            (sensor_id, value)
        )
    return {"inserted": True}
```

