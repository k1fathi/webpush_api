from sqlalchemy import Column, Integer, JSON, ForeignKey
from db.database import Base

class CEP(Base):
    __tablename__ = 'cep'

    cep_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    data = Column(JSON)
