from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext import declarative
import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256
import motor.motor_asyncio
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema


fast_mail_conf = ConnectionConfig(
    MAIL_USERNAME='Your username',
    MAIL_PASSWORD='Your password',
    MAIL_FROM='samapikanayak03@gmail.com',
    MAIL_PORT=587,
    MAIL_SERVER='smt- server',
    MAIL_FROM_NAME="Samapika",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER='templates',
)

MONGO_DETAILS = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.user_db

user_collection = database.get_collection("user_collection")


app = FastAPI()

engine = engine.create_engine('postgresql://postgres:sam@localhost/demo')
Base = declarative.declarative_base(bind=engine) 
session = sessionmaker(bind =engine, autocommit=False)

app = FastAPI()

class UserIn(BaseModel):
    name : str
    address : str
    phone_number : str
    email : str
    password : str
    confirm_password : str
    

class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String[256])
    address = sa.Column(sa.String[256])
    email = sa.Column(sa.String[256], unique=True)
    password = sa.Column(sa.String[256])

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


@app.post("/user", status_code=201)
async def create(body: UserIn, db=Depends(get_db)):
    error = False
    try:
        if body.password != body.confirm_password:
            raise HTTPException(status_code=400,detail="Password must be same")
        hash = pbkdf2_sha256.hash(body.password)
        user = User(name=body.name, address=body.address, email=body.email, password=hash)
        db.add(user)
    except:
        error = True
    else:
        db.commit()
        db.refresh(user)
        message = MessageSchema(
        subject='subject', recipients=[body.email], template_body={}, subtype="html"
        )
        fm = FastMail(fast_mail_conf)
        fm.send_message(message, template_name='templates')
        data = body.dict()
        data['password'] = hash
        await user_collection.insert_one(data)
    finally:
        if error:
            return {"status": "failed", "message": "something went wrong"}
        return {"status": "success","data": user}



Base.metadata.create_all()
#ytgftrdrtfgyuhnuyfrt
#trftyghbiytgytfyt