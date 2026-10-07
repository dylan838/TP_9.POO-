import warnings

from sqlalchemy import create_engine
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite no maneja Decimal de forma nativa y SQLAlchemy avisa de ello.
# Con 2 decimales de precisión el aviso es inofensivo (en PostgreSQL desaparece).
warnings.filterwarnings("ignore", message="Dialect sqlite.*Decimal", category=SAWarning)

SQLALCHEMY_DATABASE_URL = "sqlite:///./smartticket.db"

# check_same_thread=False es necesario en SQLite porque FastAPI
# puede atender una misma petición desde distintos hilos.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: abre una sesión por request y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
