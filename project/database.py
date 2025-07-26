from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

engine = create_engine("sqlite:///bot_db.sqlite3")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    family_info = Column(String)
    receipt_path = Column(String)
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    reminder_sent = Column(Boolean, default=False)

class QRCode(Base):
    __tablename__ = "qrcodes"
    id = Column(Integer, primary_key=True)  # 1 تا 100
    filename = Column(String)
    is_used = Column(Boolean, default=False)

Base.metadata.create_all(engine)
