# Starlette Boilerplate Project

[![Sourcery](https://img.shields.io/badge/Sourcery-refactored-blueviolet.svg)](https://sourcery.ai)
![](https://github.com/accent-starlette/boilerplate/workflows/Test,%20Build%20and%20Publish/badge.svg?branch=master)

## Getting Started

Build the container:

```bash
docker-compose build
```

Up the container:

```bash
docker-compose up
```

Setup your database by creating your first revision, you may need to add some missing imports:

```bash
docker-compose exec app sh
alembic revision --autogenerate -m "first revision"
```

Then apply it:

```bash
docker-compose exec app sh
alembic upgrade head
```

## Ready!!

The container is ready at http://localhost

## Environment Variables

### base
- ALLOWED_HOSTS
- DATABASE_URL
- DEBUG
- SECRET_KEY

### email
- EMAIL_HOST
- EMAIL_PORT
- EMAIL_DEFAULT_FROM_ADDRESS
- EMAIL_DEFAULT_FROM_NAME
- EMAIL_USERNAME
- EMAIL_PASSWORD

### aws
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_BUCKET
- AWS_REGION

### other
- SENTRY_DSN

## Formatting and Linting

Sorts imports, removes unused variables, max line length etc

```bash
docker-compose exec app ./scripts/lint
```

## Testing

Run tests and coverage

```bash
docker-compose exec app ./scripts/test
```

## New User & Example Scope

```bash
docker-compose exec app python
```

The following will just paste into the python shell to
save you copying each line.

```python
from app.db import db
from starlette_auth.tables import Scope, User
scope = Scope(code="admin", description="Full administrators access")
user = User(email='admin@example.com', first_name='Admin', last_name='User')
user.set_password('password')
user.scopes.append(scope)
user.save()
```

## Styles

npm install:

```bash
npm install
```

build css:

```bash
npm run watch-css
```
