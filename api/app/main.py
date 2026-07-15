from fastapi import FastAPI
from app.routers import users, households

app = FastAPI(title="Mealdoo API")
app.include_router(users.router)
app.include_router(households.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Mealdoo API!"}