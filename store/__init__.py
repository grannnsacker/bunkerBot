from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from store.config import PostgresConfig

Base = declarative_base()


class PostgresDB:
    def __init__(self, cfg: PostgresConfig):
        self.config = cfg
        self.factory = self._make_factory()

    def get_session(self) -> Session:
        return self.factory()

    def get_factory(self):
        return self.factory

    def _make_factory(self) -> sessionmaker:
        pg_dsn = self._get_dsn()
        engine = create_engine(pg_dsn)
        session_factory = sessionmaker(engine)
        return session_factory

    def _get_dsn(self) -> str:
        return f'postgresql://{self.config.user}:{self.config.password}@' \
               f'{self.config.host}:{self.config.port}/{self.config.db}'


postgresDB = PostgresDB(PostgresConfig())