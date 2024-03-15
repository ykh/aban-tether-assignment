# README

## Project Spec

- Python: 3.12
- Dependencies Manager: Poetry 1.8.2
- Django: 5.0.3
- Code Linter/Formatter: Ruff 0.3.2
- DB Image: PostgreSQL 16-alpine
- Cache Image: Redis 7-alpine
- Orchestration: Docker Compose

## Setup & Run Project

- Environment variables: create and update `app.env` and `db.env` files in `env_files` directory.
- Build images: `docker compose build --no-cache`
- Run App container: `docker compose up app --force-recreate`
- Run tests: `docker compose run --rm app sh -c "python manage.py test"`

## TODO List

- [x] Dockerize project.
- [x] Configure DB service using Docker.
- [x] Design ERD for required models.
- [x] Implement models based on ERDs.
- [x] Register and configure models to Django admin.
- [x] Setup Ruff.
- [x] Setup logger for Django (Using file and console).
- [x] Configure Redis service using Docker.
- [x] Implement 'order' API method.
- [x] Implement the logic of batching orders to exceed minimum settlement via exchange API.
- [x] Exceptions handling - using DRF exceptions.
- [x] Write a couple of unit tests.
- [x] Check code format by Ruff.
- [ ] Use transaction for creating new order process.
- [ ] Use Lua script for getting better performance in retrieving data from Redis.
- [ ] Review code, naming, structure, readability.
- [ ] Update/sync cached pending orders frequently - using cron job.
