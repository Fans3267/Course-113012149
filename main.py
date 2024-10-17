from fastapi import FastAPI

app = FastAPI()
class Item():
    name: str
    description: str | None = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/hello")
def read_root():
    return {"I'm not saying hello"}

@app.post("/items/")
def create_item(item: Item):
    return {"message": "Item created"}