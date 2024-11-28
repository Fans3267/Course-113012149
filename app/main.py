from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine,Column,Integer,String,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
app = FastAPI()


DATABASE_URL="sqlite:///./todos.db"
base = declarative_base()
engine = create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
SessionLocal =  sessionmaker(autocommit=False,autoflush=False,bind=engine)

class todo(base):
    __tablename__ = "todos"
    id= Column(Integer,primary_key=True,index=True)
    title = Column(String,nullable=False)
    descrption= Column(String,nullable= True)
    completed=Column(Boolean,default=False)
    sort = Column(Integer)

base.metadata.create_all(bind=engine)

class todoBase(BaseModel):
    title:str
    description:str| None=None
    completed:bool=False

class todoCreate(todoBase):
    pass

class todoresponse(todoBase):
    id:int
    class Config:
        from_attributes = True

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/todos",response_model=todoresponse)
def create_todo(todo:todoCreate,db:Session=Depends(get_db)):
    db_todo=todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos",response_model=list[todoresponse])
def read_todos(db:Session=Depends(get_db)):
    return db.query(todo).all()

@app.get("/todos/{todo_id}",response_model=todoresponse)
def read_todo(todo_id:int,db:Session=Depends(get_db)):
    db_todo=db.query(todo).filter(todo.id==todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404,details="Todo not found")
    return db_todo

@app.put("/todos/{todo_id}",response_model=todoresponse)
def update_todo(todo_id:int,todo:todoCreate,db:Session=Depends(get_db)):
    db_todo = db.query(todo).filter(todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404,details="Todo not found")
    for key,value in todo.dict().items():
        setattr(db_todo,key,value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id:int,db:Session=Depends(get_db)):
    db_todo = db.query(todo).filter(todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404,details="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"detail":"todo deleted successfully"}
