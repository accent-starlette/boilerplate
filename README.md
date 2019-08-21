# Starlette Boilerplate Project

<a href="https://travis-ci.org/accent-starlette/boilerplate">
    <img src="https://travis-ci.org/accent-starlette/boilerplate.svg?branch=master" alt="Build Status">
</a>

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
from app import db
from starlette_core.database import Session
from starlette_auth.tables import Scope, User
scope = Scope(code="admin", description="Full administrators access")
user = User(email='admin@example.com', first_name='Admin', last_name='User')
user.set_password('password')
user.scopes.append(scope)
session = Session()
session.add_all([scope, user])
session.commit()
session.close()
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
