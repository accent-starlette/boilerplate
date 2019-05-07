import pytest
from starlette.config import environ


environ['TESTING'] = 'TRUE'
