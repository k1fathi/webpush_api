from .base_model import Base, TimestampMixin
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

# Association table for User-Segment many-to-many relationship
user_segments = Table(
    'user_segments',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.user_id')),
    Column('segment_id', Integer, ForeignKey('segments.segment_id'))
)

class Segment(Base, TimestampMixin):
    __tablename__ = "segments"
    
    segment_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    
    # Relationships
    users = relationship("User", secondary=user_segments, back_populates="segments")
