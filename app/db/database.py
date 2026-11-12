from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import config

engine = create_engine(config.db_connection_string)

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session
