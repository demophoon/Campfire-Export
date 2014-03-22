from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("room.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    body = Column(Text)
    created_at = Column(DateTime)
    type = Column(Text)


class Room(Base):
    __tablename__ = 'room'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    topic = Column(String)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)

    messages = relationship("Message", backref="room")

    def __repr__(self):
        return "<Campfire.Room '%s' with id: %d>" % (self.name, self.id)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email_address = Column(String)
    created_at = Column(DateTime)
    type = Column(Text)
    avatar_url = Column(Text)

    messages = relationship("Message", backref="user")
