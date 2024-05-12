from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

#tablas
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing ID starting from 0
    name = Column(String(255), nullable=False)

class Emails(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    email = Column(String(255), nullable=False)
    user = relationship("Users", backref="emails")  # Relationship with User table
