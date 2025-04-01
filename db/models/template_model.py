from .base_model import Base, TimestampMixin
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

class Template(Base, TimestampMixin):
    __tablename__ = "templates"
    
    template_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    variables = Column(JSON)  # ["name", "product", etc.]
    webpushes = relationship("WebPush", back_populates="template")
