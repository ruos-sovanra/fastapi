from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session as DBSession
from typing import List
from telethon import TelegramClient, events

# Database setup
DATABASE_URL = "postgresql://postgres:lyhou123@localhost/flash"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# Message model
class Message(Base):
    __tablename__ = 'messages1'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    content = Column(String)
    timestamp = Column(DateTime)


# Create tables
Base.metadata.create_all(engine)

# FastAPI setup
app = FastAPI()

# Telethon setup
from config import DESTINATION, API_ID, API_HASH, SESSION, CHATS, KEY_WORDS

client = TelegramClient(SESSION, API_ID, API_HASH)


# Event handler to handle new messages
@client.on(events.NewMessage(chats=CHATS))
async def new_order(event):
    try:
        print("Received event message:", event)
        message_content = event.message.message
        print(f'Received a new message: {message_content} and this is chat id = {event.id}')

        # Insert message into database
        session = Session()
        new_message = Message(chat_id=event.id, content=message_content, timestamp=datetime.now())
        session.add(new_message)
        session.commit()
        session.close()

        contain_key_word = any(key_word in message_content for key_word in KEY_WORDS)

        if contain_key_word:
            print('Message contains a keyword, forwarding...')
            await client.forward_messages(DESTINATION, event.message)
        else:
            print('Message does not contain any of the specified keywords.')

    except Exception as ex:
        print(f'Exception: {ex}')


# Endpoint to fetch messages
# @app.get('/messages/', response_model=List[Message])
# def get_messages(skip: int = 0, limit: int = 10, db: DBSession = Depends(Session)):
#     return db.query(Message).offset(skip).limit(limit).all()


if __name__ == '__main__':
    print("Program is running...")

    # Start Telethon client
    client.start()
    client.run_until_disconnected()
