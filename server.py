import uvicorn
import json
import os
import shutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()
connections = []

# Yükleme dizinini oluştur
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Yüklenen dosyaları dışa sunmak için statik dizin bağlaması
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
async def get_index():
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(file_path)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # NOT: Üretim ortamında UUID kullanılarak dosya çakışmaları (collision) engellenmelidir.
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    return {"url": f"/uploads/{file.filename}", "filename": file.filename}

@app.websocket("/")
async def ws(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            for connection in connections:
                await connection.send_text(message)
    except WebSocketDisconnect:
        connections.remove(websocket)
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        if websocket in connections:
            connections.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
