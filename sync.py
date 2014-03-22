import logging
import ConfigParser
import sys
from time import (strptime, mktime)
from datetime import datetime, timedelta

from pinder import Campfire

from models import Base, Message, Room, User
from sqlalchemy import desc, engine_from_config
from sqlalchemy.orm import sessionmaker, scoped_session


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def convert_to_datetime(date_str):
    timeformat = "%Y/%m/%d %H:%M:%S +0000"
    return datetime.fromtimestamp(
        mktime(strptime(date_str, timeformat)))


def get_rooms(campfire, DBSession):
    for room in campfire.rooms():
        if DBSession.query(Room).filter(Room.id == room['id']).first():
            continue
        room_obj = Room()
        room_obj.id = room['id']
        room_obj.name = room['name']
        room_obj.topic = room['topic']
        room_obj.updated_at = convert_to_datetime(room['updated_at'])
        room_obj.created_at = convert_to_datetime(room['created_at'])
        DBSession.add(room_obj)
        DBSession.flush()
    DBSession.commit()


def get_user(campfire, DBSession, user_id):
    user = campfire.user(user_id)['user']
    user_obj = User()
    user_obj.id = user['id']
    user_obj.name = user['name']
    user_obj.email_address = user['email_address']
    user_obj.created_at = convert_to_datetime(user['created_at'])
    user_obj.type = user['type']
    user_obj.avatar_url = user['avatar_url']
    DBSession.add(user_obj)
    DBSession.flush()


def add_message(DBSession, message):
    m = Message()
    m.id = message['id']
    m.room_id = message['room_id']
    m.user_id = message['user_id']
    m.body = message['body']
    m.created_at = convert_to_datetime(message['created_at'])
    m.type = message.get('type')
    m.starred = message['user_id']
    DBSession.add(m)
    DBSession.flush()


def main(config, DBSession):

    subdomain = config.get("Campfire", "subdomain")
    token = config.get("Campfire", "token")

    c = Campfire(subdomain, token)

    get_rooms(c, DBSession)

    today = datetime.today().date()
    for room in DBSession.query(Room).all():
        logger.info("Working on room %s" % room.name)
        current_room = c.room(room.id)
        current_room.join()
        current_date = DBSession.query(Message).filter(
            Message.room_id == room.id
        ).order_by(
            desc(Message.created_at)
        ).first()
        if not(current_date):
            current_date = room
        current_date = current_date.created_at.date()
        while current_date <= today:
            transcript = []
            try:
                transcript = current_room.transcript(current_date)
            except Exception as e:
                logger.warn("Exception while retrieving transcript. %s" % e)
            logger.info("Working on room %s (%s): Messages %d" % (
                room.name, str(current_date), len(transcript)))
            for message in transcript:
                if message['user_id'] and not(DBSession.query(User).filter(
                    User.id == message['user_id']).first()):
                    get_user(c, DBSession, message['user_id'])

                if not(DBSession.query(Message).filter(Message.id == message['id']).first()):
                    add_message(DBSession, message)
            DBSession.commit()

            current_date += timedelta(days=1)

    DBSession.flush()
    DBSession.commit()


def setup_database_session(config):
    engine = engine_from_config(config)
    DBSession = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(engine)
    return DBSession


def ConfigSectionMap(Config, section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
        except:
            dict1[option] = None
    return dict1

if __name__ == "__main__":
    args = sys.argv[1:]
    config = args[0]
    Config = ConfigParser.ConfigParser()
    Config.read(config)
    DBSession = setup_database_session(ConfigSectionMap(Config, "SqlAlchemy"))
    main(Config, DBSession)
