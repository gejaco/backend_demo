from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import websockets
import asyncio
import os
import json
import logging

print("Startup message")

app = FastAPI()
logger = logging.getLogger("uvicorn.error")
#DEEPGRAM_API_KEY = os.environ.get("11511bdebd666816f3575dfa0e2d8031ccdbc605")  # Store your key as an environment variable
logger.info("logger Message here")
DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")

if not DEEPGRAM_API_KEY:
    raise RuntimeError("Deepgram API key not set in environment variable DEEPGRAM_API_KEY")

DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen?punctuate=true"

@app.websocket("/ws/deepgram")
async def proxy_to_deepgram(websocket: WebSocket):
    logger.info("WebSocket endpoint called")
    await websocket.accept()
    try:
        async with websockets.connect(
            DEEPGRAM_WS_URL,
            extra_headers ={
                "Authorization": f"Token {DEEPGRAM_API_KEY}"
            }
        ) as dg_socket:
            async def from_client_to_deepgram():
                print("WebSocket: entering receive loop")
                logger.info("logger WebSocket: entering receive loop")
                try:
                    while True:
                        data = await websocket.receive_bytes() 
                        print('Received', len(data), 'bytes from client')                       
                        logger.info('logger Received bytes from client')                       
                        await dg_socket.send(data)
                except WebSocketDisconnect as e:
                    # This prints details about the disconnect event
                    print(f"WebSocketDisconnect: code={e.code}, reason={getattr(e, 'reason', None)}")
                    await dg_socket.close()
                except Exception as e:
                    print("Client->Deepgram error:", e)
                    await dg_socket.close()

            async def from_deepgram_to_client():
                try:
                    async for dg_data in dg_socket:
                        try:
                            packet = json.loads(dg_data)
                            transcript = packet.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
                            if transcript:
                                print(transcript)
                        except Exception as e:
                            print("Error extracting transcript:", e)

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
