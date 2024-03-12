from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define a Pydantic model for request and response data
class Detection(BaseModel):
    name: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/detect/")
async def detect_face(detection: Detection):
    print(f"Wajah Terdeteksi: {detection.name}")
    # Lakukan tindakan berikutnya sesuai kebutuhan
    return {"message": "Data received"}
