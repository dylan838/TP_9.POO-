from sqlalchemy import Column, ForeignKey, Integer, Numeric, String

from database import Base


class Sector(Base):
    __tablename__ = "sectores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)  # precio unitario por entrada
    capacidad = Column(Integer, nullable=False)  # cantidad total de entradas
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
