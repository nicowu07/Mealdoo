from fastapi import FastAPI
from app.routers import users

app = FastAPI(title="Mealdoo API")
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Mealdoo API!"}