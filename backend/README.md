## Development

### How to run dev server

1. Build the docker image:

```bash
docker-compose build
```

2. Copy the `.env.template` file to `.env`:

```bash
cp .env.example .env
```

3. Run the devtools contaiver:

```bash
make start-devtools
```

4. Run migrations:

```bash
make run-api-command args="migrate"
```

5. Create a user:

```bash
make run-api-command args="create_user"
```

### Development helpers

1. Spin mock feed server:

```bash
docker compose up mock_feed_server
```
Now you can access the feed at
[http://localhost:8001?quantity=10](http://localhost:8001?quantity=10)

2. Manually send stream events:

First, you need api token. You can get it by running:

```bash
make run-api-command args="create_access_token --sub=<user_id> --expires_minutes=5256000"  # 10 years
```

Then you can send stream events:

```bash
make run-module args="development.send_stream_event --stream-slug=<stream slug> --api-token=<api_token>"
```

### Working with polylith

1. Check dependencies in project:

```bash
make poetry args="poly check --alias python-jose=jose"
```

2. Sow info about libs:

```bash
make poetry args="poly libs --alias python-jose=jose"
```
