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
make run-command args="migrate"
```

5. Create a user:

```bash
make run-command args="create_user"
```
