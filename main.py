import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()
load_dotenv()

@app.get("/")
async def root():
    return {"message": "Hello World"}


bot_token = os.getenv('BOT_TOKEN')
secret_token = os.getenv("SECRET_TOKEN")

print(" MAIN PROGRAM INITIALIZED")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8181)
