# from datetime import datetime
#
# import uvicorn
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from fastapi import FastAPI, Depends
# from sqlalchemy.orm import Session as DBSession
# from typing import List
# from telethon import TelegramClient, events
#
# # Database setup
# DATABASE_URL = "postgresql://postgres:lyhou123@localhost/user"
# engine = create_engine(DATABASE_URL, echo=True)
# Session = sessionmaker(bind=engine)
# Base = declarative_base()
#
#
# # Message model
# class Message(Base):
#     __tablename__ = 'transactions'
#
#     id = Column(Integer, primary_key=True)
#     account_name = Column(String)
#     amount = Column(String)
#     transaction_id = Column(String)
#     approval_code = Column(String)
#     remark = Column(String)
#     timestamp = Column(DateTime)
#
#
# # Create tables
# Base.metadata.create_all(engine)
#
# # Telethon setup
# from config import DESTINATION, API_ID, API_HASH, SESSION, CHATS, KEY_WORDS
#
# client = TelegramClient(SESSION, API_ID, API_HASH)
#
# app = FastAPI()
#
#
# # Event handler to handle new messages
# @client.on(events.NewMessage(chats=CHATS))
# async def new_order(event):
#     try:
#         print("Received event message:", event)
#         message_content = event.message.message
#         print(f'Received a new message: {message_content} and this is chat id = {event.id}')
#
#         # Insert message into database
#         session = Session()
#         new_message = Message(chat_id=event.id, content=message_content, timestamp=datetime.now())
#         session.add(new_message)
#         session.commit()
#         session.close()
#
#         contain_key_word = any(key_word in message_content for key_word in KEY_WORDS)
#
#         if contain_key_word:
#             print('Message contains a keyword, forwarding...')
#             await client.forward_messages(DESTINATION, event.message)
#         else:
#             print('Message does not contain any of the specified keywords.')
#
#     except Exception as ex:
#         print(f'Exception: {ex}')
#
#
# # Pydantic model for response
# class MessageResponse(BaseModel):
#     id: int
#     chat_id: int
#     content: str
#     timestamp: datetime
#
#
# # Dependency to get DB session
# def get_db():
#     db = Session()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# # Endpoint to fetch messages
# @app.get('/test', response_model=List[MessageResponse])
# def get_messages(skip: int = 0, limit: int = 10, db: DBSession = Depends(get_db)):
#     messages = db.query(Message).offset(skip).limit(limit).all()
#     return [
#         MessageResponse(id=message.id, chat_id=message.chat_id, content=message.content, timestamp=message.timestamp)
#         for message in messages
#     ]
#
#
# if __name__ == '__main__':
#     print("Program is running...")
#
#     # Start Telethon client
#     client.start()
#
#     # Run FastAPI with uvicorn server
#     # uvicorn.run(app, host='0.0.0.0', port=8000)
#     client.run_until_disconnected()


from datetime import datetime
import re
import uvicorn
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as DBSession
from fastapi import FastAPI, Depends
from typing import List
from telethon import TelegramClient, events

# Database setup
DATABASE_URL = "postgresql://postgres:lyhou123@localhost/user"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# Transaction model
class Transaction(Base):
    __tablename__ = 'transactions1'

    id = Column(Integer, primary_key=True)
    account_name = Column(String)
    amount = Column(String)
    transaction_id = Column(String)
    approval_code = Column(String)
    remark = Column(String)
    hour = Column(String)  # New column for hour
    bank_name = Column(String)  # New column for bank name
    timestamp = Column(DateTime)


# Create tables
Base.metadata.create_all(engine)

# Telethon setup
from config import DESTINATION, API_ID, API_HASH, SESSION, CHATS, KEY_WORDS

client = TelegramClient(SESSION, API_ID, API_HASH)

app = FastAPI()


# Event handler to handle new messages
@client.on(events.NewMessage(chats=CHATS))
async def new_order(event):
    try:
        print("Received event message:", event)
        message_content = event.message.message
        print(f'Received a new message: {message_content} and this is chat id = {event.id}')

        # Insert message into database
        session = Session()
        new_message = Transaction(
            account_name=None,  # Placeholder
            amount=None,  # Placeholder
            transaction_id=None,  # Placeholder
            approval_code=None,  # Placeholder
            remark=None,  # Placeholder
            hour=None,  # Placeholder
            bank_name=None,  # Placeholder
            timestamp=datetime.now()
        )

        # Extract information using regex
        amount_match = re.search(r'[៛\$]\d+', message_content)
        account_name_match = re.search(r'(?<=paid by )[\w\s]+(?= \(\*\d{3}\))', message_content)
        transaction_id_match = re.search(r'(?<=Trx. ID: )\d+', message_content)
        approval_code_match = re.search(r'(?<=APV: )\d+', message_content)
        remark_match = re.search(r'(?<=Remark: ).*?(?=\.)', message_content)
        hour_match = re.search(r'\d{1,2}:\d{2} [AP]M', message_content)
        bank_name_match = re.search(r'via \w+ \w+', message_content)

        new_message.amount = amount_match.group(0) if amount_match else None
        new_message.account_name = account_name_match.group(0) if account_name_match else None
        new_message.transaction_id = transaction_id_match.group(0) if transaction_id_match else None
        new_message.approval_code = approval_code_match.group(0) if approval_code_match else None
        new_message.remark = remark_match.group(0) if remark_match else None
        new_message.hour = hour_match.group(0) if hour_match else None
        new_message.bank_name = bank_name_match.group(0) if bank_name_match else None

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


# Pydantic model for response
class TransactionResponse(BaseModel):
    id: int
    account_name: str
    amount: str
    transaction_id: str
    approval_code: str
    remark: str
    timestamp: datetime


# Dependency to get DB session
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# Endpoint to fetch transactions
@app.get('/transactions', response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 10, db: DBSession = Depends(get_db)):
    transactions = db.query(Transaction).offset(skip).limit(limit).all()
    return [
        TransactionResponse(
            id=transaction.id,
            account_name=transaction.account_name,
            amount=transaction.amount,
            transaction_id=transaction.transaction_id,
            approval_code=transaction.approval_code,
            remark=transaction.remark,
            timestamp=transaction.timestamp
        ) for transaction in transactions
    ]


if __name__ == '__main__':
    print("Program is running...")

    # Start Telethon client
    client.start()

    # Run FastAPI with uvicorn server
    # Comment out uvicorn.run as it will not run in this script
    # uvicorn.run(app, host='0.0.0.0', port=8000)
    client.run_until_disconnected()
