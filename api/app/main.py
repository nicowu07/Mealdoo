from fastapi import FastAPI

app = FastAPI(title="Mealdoo API")

@app.get("/")
def root():
    return {"message": "Welcome to the Mealdoo API!"}