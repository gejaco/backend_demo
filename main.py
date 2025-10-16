from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import websockets
import asyncio
import os

app = FastAPI()
#DEEPGRAM_API_KEY = os.environ.get("11511bdebd666816f3575dfa0e2d8031ccdbc605")  # Store your key as an environment variable
DEEPGRAM_API_KEY = "11511bdebd666816f3575dfa0e2d8031ccdbc605"
DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen?punctuate=true"

@app.websocket("/ws/deepgram")
async def proxy_to_deepgram(websocket: WebSocket):
    await websocket.accept()
    try:
        async with websockets.connect(
            DEEPGRAM_WS_URL,
            extra_headers ={
                "Authorization": f"Token {DEEPGRAM_API_KEY}"
            }
        ) as dg_socket:
            async def from_client_to_deepgram():
                try:
                    while True:
                        data = await websocket.receive_bytes()                        
                        await dg_socket.send(data)
                except WebSocketDisconnect:
                    await dg_socket.close()
                except Exception as e:
                    print("Client->Deepgram error:", e)

            async def from_deepgram_to_client():
                try:
                    async for dg_data in dg_socket:
                        print("Raw Deepgram data:", dg_data)
                        await websocket.send_text(dg_data)
                except Exception as e:
                    print("Deepgram->Client error:", e)
                    await websocket.close()

            await asyncio.gather(from_client_to_deepgram(), from_deepgram_to_client())

    except Exception as e:
        print("Proxy error:", e)
        await websocket.close()

@app.get("/")
async def root():
    return {"message": "Proxy is running. Connect websockets to /ws/deepgram"}
