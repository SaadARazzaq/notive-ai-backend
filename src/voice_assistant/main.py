# # # src/voice_assistant/main.py
# # import asyncio
# # import json
# # import logging
# # import os

# # import pygame
# # import websockets
# # from websockets.exceptions import ConnectionClosedError

# # from voice_assistant.config import (
# #     PREFIX_PADDING_MS,
# #     SESSION_INSTRUCTIONS,
# #     SILENCE_DURATION_MS,
# #     SILENCE_THRESHOLD,
# # )
# # from voice_assistant.microphone import AsyncMicrophone
# # from voice_assistant.tools import TOOL_SCHEMAS
# # from voice_assistant.utils import base64_encode_audio
# # from voice_assistant.utils.log_utils import log_ws_event
# # from voice_assistant.visual_interface import (
# #     VisualInterface,
# #     run_visual_interface,
# # )
# # from voice_assistant.websocket_handler import process_ws_messages

# # # Set up logging
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
# #     datefmt="%H:%M:%S",
# # )
# # logger = logging.getLogger(__name__)


# # async def realtime_api():
# #     while True:
# #         try:
# #             api_key = os.getenv("OPENAI_API_KEY")
# #             if not api_key:
# #                 logger.error("Please set the OPENAI_API_KEY in your .env file.")
# #                 return

# #             exit_event = asyncio.Event()

# #             url = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17"
# #             headers = {
# #                 "Authorization": f"Bearer {api_key}",
# #                 "OpenAI-Beta": "realtime=v1",
# #             }

# #             mic = AsyncMicrophone()
# #             visual_interface = VisualInterface()

# #             async with websockets.connect(url, extra_headers=headers) as websocket:
# #                 logger.info("Connected to the server.")
# #                 # Initialize the session with voice capabilities and tools
# #                 session_update = {
# #                     "type": "session.update",
# #                     "session": {
# #                         "modalities": ["text", "audio"],
# #                         "instructions": SESSION_INSTRUCTIONS,
# #                         "voice": "alloy",
# #                         "input_audio_format": "pcm16",
# #                         "output_audio_format": "pcm16",
# #                         "turn_detection": {
# #                             "type": "server_vad",
# #                             "threshold": SILENCE_THRESHOLD,
# #                             "prefix_padding_ms": PREFIX_PADDING_MS,
# #                             "silence_duration_ms": SILENCE_DURATION_MS,
# #                         },
# #                         "tools": TOOL_SCHEMAS,
# #                     },
# #                 }
# #                 log_ws_event("outgoing", session_update)
# #                 await websocket.send(json.dumps(session_update))

# #                 ws_task = asyncio.create_task(
# #                     process_ws_messages(websocket, mic, visual_interface)
# #                 )
# #                 visual_task = asyncio.create_task(
# #                     run_visual_interface(visual_interface)
# #                 )

# #                 logger.info(
# #                     "Conversation started. Speak freely, and the assistant will respond."
# #                 )
# #                 mic.start_recording()
# #                 logger.info("Recording started. Listening for speech...")

# #                 try:
# #                     while not exit_event.is_set():
# #                         await asyncio.sleep(0.01)  # Small delay to reduce CPU usage
# #                         if not mic.is_receiving:
# #                             audio_data = mic.get_audio_data()
# #                             if audio_data:
# #                                 base64_audio = base64_encode_audio(audio_data)
# #                                 if base64_audio:
# #                                     audio_event = {
# #                                         "type": "input_audio_buffer.append",
# #                                         "audio": base64_audio,
# #                                     }
# #                                     log_ws_event("outgoing", audio_event)
# #                                     await websocket.send(json.dumps(audio_event))
# #                                     # Update energy for visualization
# #                                     visual_interface.process_audio_data(audio_data)
# #                                 else:
# #                                     logger.debug("No audio data to send")
# #                 except KeyboardInterrupt:
# #                     logger.info("Keyboard interrupt received. Closing the connection.")
# #                 except Exception as e:
# #                     logger.exception(
# #                         f"An unexpected error occurred in the main loop: {e}"
# #                     )
# #                 finally:
# #                     exit_event.set()
# #                     mic.stop_recording()
# #                     mic.close()
# #                     await websocket.close()
# #                     visual_interface.set_active(False)

# #                 # Wait for the WebSocket processing task to complete
# #                 try:
# #                     await ws_task
# #                     await visual_task
# #                 except Exception as e:
# #                     logging.exception(f"Error in WebSocket processing task: {e}")

# #             # If execution reaches here without exceptions, exit the loop
# #             break
# #         except ConnectionClosedError as e:
# #             if "keepalive ping timeout" in str(e):
# #                 logging.warning(
# #                     "WebSocket connection lost due to keepalive ping timeout. Reconnecting..."
# #                 )
# #                 await asyncio.sleep(1)  # Wait before reconnecting
# #                 continue  # Retry the connection
# #             logging.exception("WebSocket connection closed unexpectedly.")
# #             break  # Exit the loop on other connection errors
# #         except Exception as e:
# #             logging.exception(f"An unexpected error occurred: {e}")
# #             break  # Exit the loop on unexpected exceptions
# #         finally:
# #             if "mic" in locals():
# #                 mic.stop_recording()
# #                 mic.close()
# #             if "websocket" in locals():
# #                 await websocket.close()
# #             pygame.quit()


# # async def main_async():
# #     await realtime_api()


# # def main():
# #     try:
# #         asyncio.run(main_async())
# #     except KeyboardInterrupt:
# #         logger.info("Program terminated by user")
# #     except Exception as e:
# #         logger.exception(f"An unexpected error occurred: {e}")


# # if __name__ == "__main__":
# #     print("Press Ctrl+C to exit the program.")
# #     main()


# # --------------------------------------------------

# # ## main.py without fast api implementation working


# import asyncio
# import json
# import logging
# import os

# import websockets
# from websockets.exceptions import ConnectionClosedError

# from voice_assistant.config import (
#     PREFIX_PADDING_MS,
#     SESSION_INSTRUCTIONS,
#     SILENCE_DURATION_MS,
#     SILENCE_THRESHOLD,
# )
# from voice_assistant.microphone import AsyncMicrophone
# from voice_assistant.tools import TOOL_SCHEMAS
# from voice_assistant.utils import base64_encode_audio
# from voice_assistant.utils.log_utils import log_ws_event
# from voice_assistant.websocket_handler import process_ws_messages

# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger(__name__)


# def get_user_voice_preference():
#     """Prompt the user to select a voice."""
#     print("Please select a voice for the assistant:")
#     print("1. Ballad (Male)")
#     print("2. Echo (Male)")
#     print("3. Ash (Male)")
#     print()
#     print("4. Coral (Female)")
#     print("5. Sage (Female)")
#     print("6. Shimmer (Female)")

#     while True:
#         choice = input("Enter the number corresponding to your preferred voice: ").strip()
#         if choice in ["1", "2", "3", "4", "5", "6"]:
#             break
#         print("Invalid choice. Please enter a number between 1 and 6.")

#     voice_mapping = {
#         "1": "ballad",
#         "2": "echo",
#         "3": "ash",
#         "4": "coral",
#         "5": "sage",
#         "6": "shimmer",
#     }
#     return voice_mapping[choice]


# async def realtime_api(voice: str):
#     while True:
#         try:
#             api_key = os.getenv("OPENAI_API_KEY")
#             if not api_key:
#                 logger.error("Please set the OPENAI_API_KEY in your .env file.")
#                 return

#             exit_event = asyncio.Event()

#             url = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17"
#             headers = {
#                 "Authorization": f"Bearer {api_key}",
#                 "OpenAI-Beta": "realtime=v1",
#             }

#             mic = AsyncMicrophone()

#             async with websockets.connect(url, extra_headers=headers) as websocket:
#                 logger.info("Connected to the server.")
#                 # Initialize the session with voice capabilities and tools
#                 session_update = {
#                     "type": "session.update",
#                     "session": {
#                         "modalities": ["text", "audio"],
#                         "instructions": SESSION_INSTRUCTIONS,
#                         "voice": voice,  # Use the selected voice
#                         "input_audio_format": "pcm16",
#                         "output_audio_format": "pcm16",
#                         "turn_detection": {
#                             "type": "server_vad",
#                             "threshold": SILENCE_THRESHOLD,
#                             "prefix_padding_ms": PREFIX_PADDING_MS,
#                             "silence_duration_ms": SILENCE_DURATION_MS,
#                         },
#                         "tools": TOOL_SCHEMAS,
#                     },
#                 }
#                 log_ws_event("outgoing", session_update)
#                 await websocket.send(json.dumps(session_update))

#                 ws_task = asyncio.create_task(
#                     process_ws_messages(websocket, mic)
#                 )

#                 logger.info(
#                     "Conversation started. Speak freely, and the assistant will respond."
#                 )
#                 mic.start_recording()
#                 logger.info("Recording started. Listening for speech...")

#                 try:
#                     while not exit_event.is_set():
#                         await asyncio.sleep(0.01)  # Small delay to reduce CPU usage
#                         if not mic.is_receiving:
#                             audio_data = mic.get_audio_data()
#                             if audio_data:
#                                 base64_audio = base64_encode_audio(audio_data)
#                                 if base64_audio:
#                                     audio_event = {
#                                         "type": "input_audio_buffer.append",
#                                         "audio": base64_audio,
#                                     }
#                                     log_ws_event("outgoing", audio_event)
#                                     await websocket.send(json.dumps(audio_event))
#                                 else:
#                                     logger.debug("No audio data to send")
#                 except KeyboardInterrupt:
#                     logger.info("Keyboard interrupt received. Closing the connection.")
#                 except Exception as e:
#                     logger.exception(
#                         f"An unexpected error occurred in the main loop: {e}"
#                     )
#                 finally:
#                     exit_event.set()
#                     mic.stop_recording()
#                     mic.close()
#                     await websocket.close()

#                 # Wait for the WebSocket processing task to complete
#                 try:
#                     await ws_task
#                     await visual_task
#                 except Exception as e:
#                     logging.exception(f"Error in WebSocket processing task: {e}")

#             # If execution reaches here without exceptions, exit the loop
#             break
#         except ConnectionClosedError as e:
#             if "keepalive ping timeout" in str(e):
#                 logging.warning(
#                     "WebSocket connection lost due to keepalive ping timeout. Reconnecting..."
#                 )
#                 await asyncio.sleep(1)  # Wait before reconnecting
#                 continue  # Retry the connection
#             logging.exception("WebSocket connection closed unexpectedly.")
#             break  # Exit the loop on other connection errors
#         except Exception as e:
#             logging.exception(f"An unexpected error occurred: {e}")
#             break  # Exit the loop on unexpected exceptions
#         finally:
#             if "mic" in locals():
#                 mic.stop_recording()
#                 mic.close()
#             if "websocket" in locals():
#                 await websocket.close()


# async def main_async():
#     voice = get_user_voice_preference()
#     await realtime_api(voice)


# def main():
#     try:
#         asyncio.run(main_async())
#     except KeyboardInterrupt:
#         logger.info("Program terminated by user")
#     except Exception as e:
#         logger.exception(f"An unexpected error occurred: {e}")


# if __name__ == "__main__":
#     print("Press Ctrl+C to exit the program.")
#     main()


# # --------------------------------------------------------

## main.py with fast api implementation not working

# import asyncio
# import json
# import logging
# import os
# from contextlib import asynccontextmanager
# from typing import Optional

# import uvicorn
# import websockets
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from websockets.exceptions import ConnectionClosedError

# from voice_assistant.config import (
#     PREFIX_PADDING_MS,
#     SESSION_INSTRUCTIONS,
#     SILENCE_DURATION_MS,
#     SILENCE_THRESHOLD,
# )
# from voice_assistant.microphone import AsyncMicrophone
# from voice_assistant.tools import TOOL_SCHEMAS
# from voice_assistant.utils import base64_encode_audio
# from voice_assistant.utils.log_utils import log_ws_event
# from voice_assistant.websocket_handler import process_ws_messages

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
#     datefmt="%H:%M:%S",
# )
# logger = logging.getLogger(__name__)

# # --- FastAPI Models ---
# class VoiceRequest(BaseModel):
#     voice: str

# class AudioRequest(BaseModel):
#     audio_base64: str

# # --- Application State ---
# class AppState:
#     def __init__(self):
#         self.voice = "shimmer"  # Default voice
#         self.mic: Optional[AsyncMicrophone] = None
#         self.websocket = None
#         self.realtime_task = None
#         self.message_queue = asyncio.Queue()
#         self.lock = asyncio.Lock()
#         self.exit_event = asyncio.Event()
#         self.recording_enabled = False

# app_state = AppState()

# # --- FastAPI Lifespan Management ---
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Initialize realtime connection
#     app_state.realtime_task = asyncio.create_task(realtime_api())
#     yield
#     # Cleanup on shutdown
#     app_state.exit_event.set()
#     if app_state.realtime_task:
#         app_state.realtime_task.cancel()
#     if app_state.mic:
#         app_state.mic.stop_recording()
#         app_state.mic.close()

# app = FastAPI(lifespan=lifespan)

# # --- API Endpoints ---
# @app.post("/set_voice")
# async def set_voice(request: VoiceRequest):
#     valid_voices = ["ballad", "echo", "ash", "coral", "sage", "shimmer"]
#     if request.voice not in valid_voices:
#         raise HTTPException(status_code=400, detail="Invalid voice selection")
    
#     async with app_state.lock:
#         app_state.voice = request.voice
#         logger.info(f"Voice changed to: {request.voice}")
    
#     # Restart connection with new voice
#     if app_state.realtime_task:
#         app_state.realtime_task.cancel()
#     app_state.realtime_task = asyncio.create_task(realtime_api())
    
#     return {"status": "voice_changed", "new_voice": request.voice}

# @app.post("/start_recording")
# async def start_recording():
#     if not app_state.mic:
#         raise HTTPException(status_code=400, detail="Microphone not initialized")
    
#     app_state.mic.start_recording()
#     app_state.recording_enabled = True
#     logger.info("Recording started via API")
#     return {"status": "recording_started"}

# @app.post("/stop_recording")
# async def stop_recording():
#     if not app_state.mic:
#         raise HTTPException(status_code=400, detail="Microphone not initialized")
    
#     app_state.mic.stop_recording()
#     app_state.recording_enabled = False
#     logger.info("Recording stopped via API")
#     return {"status": "recording_stopped"}

# @app.post("/process_audio")
# async def process_audio(request: AudioRequest):
#     audio_event = {
#         "type": "input_audio_buffer.append",
#         "audio": request.audio_base64,
#     }
#     await app_state.message_queue.put(json.dumps(audio_event))
#     return {"status": "audio_processed"}

# @app.get("/status")
# async def get_status():
#     return {
#         "voice": app_state.voice,
#         "recording": app_state.recording_enabled,
#         "connected": app_state.websocket.open if app_state.websocket else False
#     }

# # --- Core Functionality ---
# async def realtime_api():
#     while not app_state.exit_event.is_set():
#         try:
#             api_key = os.getenv("OPENAI_API_KEY")
#             if not api_key:
#                 logger.error("OPENAI_API_KEY not set in environment")
#                 await asyncio.sleep(5)
#                 continue

#             url = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17"
#             headers = {
#                 "Authorization": f"Bearer {api_key}",
#                 "OpenAI-Beta": "realtime=v1",
#             }

#             async with websockets.connect(url, extra_headers=headers) as ws:
#                 app_state.websocket = ws
#                 logger.info("Connected to OpenAI WebSocket")

#                 # Initialize session
#                 session_update = {
#                     "type": "session.update",
#                     "session": {
#                         "modalities": ["text", "audio"],
#                         "instructions": SESSION_INSTRUCTIONS,
#                         "voice": app_state.voice,
#                         "input_audio_format": "pcm16",
#                         "output_audio_format": "pcm16",
#                         "turn_detection": {
#                             "type": "server_vad",
#                             "threshold": SILENCE_THRESHOLD,
#                             "prefix_padding_ms": PREFIX_PADDING_MS,
#                             "silence_duration_ms": SILENCE_DURATION_MS,
#                         },
#                         "tools": TOOL_SCHEMAS,
#                     }
#                 }
#                 log_ws_event("outgoing", session_update)
#                 await ws.send(json.dumps(session_update))

#                 # Initialize microphone
#                 app_state.mic = AsyncMicrophone()

#                 # Start processing tasks
#                 ws_task = asyncio.create_task(process_ws_messages(ws, app_state.mic))
#                 sender_task = asyncio.create_task(process_message_queue(ws))

#                 try:
#                     while not app_state.exit_event.is_set():
#                         if app_state.recording_enabled and app_state.mic.is_receiving:
#                             audio_data = app_state.mic.get_audio_data()
#                             if audio_data:
#                                 base64_audio = base64_encode_audio(audio_data)
#                                 if base64_audio:
#                                     await ws.send(json.dumps({
#                                         "type": "input_audio_buffer.append",
#                                         "audio": base64_audio
#                                     }))
#                         await asyncio.sleep(0.01)

#                 except KeyboardInterrupt:
#                     logger.info("Keyboard interrupt received")
#                 finally:
#                     sender_task.cancel()
#                     ws_task.cancel()
#                     app_state.mic.stop_recording()
#                     await ws.close()

#         except ConnectionClosedError as e:
#             logger.warning(f"Connection closed: {e}")
#             await asyncio.sleep(1)
#         except Exception as e:
#             logger.error(f"Error in realtime API: {e}")
#             await asyncio.sleep(1)

# async def process_message_queue(ws):
#     while True:
#         message = await app_state.message_queue.get()
#         await ws.send(message)
#         logger.debug("Sent queued message to WebSocket")

# # --- Main Execution ---
# async def main():
#     config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
#     server = uvicorn.Server(config)
#     await server.serve()

# if __name__ == "__main__":
#     asyncio.run(main())


# # ------------------------------------------------------------

# # main.py with flask implementation

# # src/voice_assistant/main.py

#------------------
#------------------

import asyncio
import json
import logging
import os
from threading import Lock, Thread
from typing import Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import websockets
from dotenv import load_dotenv
from websockets.exceptions import ConnectionClosedError

from voice_assistant.config import (
    PREFIX_PADDING_MS,
    SESSION_INSTRUCTIONS,
    SILENCE_DURATION_MS,
    SILENCE_THRESHOLD,
)
from voice_assistant.microphone import AsyncMicrophone
from voice_assistant.tools import TOOL_SCHEMAS
from voice_assistant.utils import base64_encode_audio
from voice_assistant.utils.log_utils import log_ws_event
from voice_assistant.websocket_handler import process_ws_messages

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Maximum debug logging
    format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# --- Application State ---
class AppState:
    def __init__(self):
        self.voice = "shimmer"
        self.mic: Optional[AsyncMicrophone] = None
        self.websocket = None
        self.message_queue = asyncio.Queue()
        self.lock = Lock()
        self.exit_event = asyncio.Event()
        self.recording_enabled = False

app_state = AppState()

# --- API Routes ---
# @app.route("/set_voice", methods=["POST"])
# def set_voice():
#     """Set the assistant's voice."""
#     data = request.get_json()
#     voice = data.get("voice")
#     valid_voices = ["ballad", "echo", "ash", "coral", "sage", "shimmer"]

#     logger.debug(f"Received request to set voice: {voice}")

#     if voice not in valid_voices:
#         logger.warning("Invalid voice selection attempted.")
#         return jsonify({"error": "Invalid voice selection"}), 400

#     app_state.voice = voice
#     logger.info(f"Voice changed to: {voice}")

#     socketio.emit("status_update", {"voice": voice, "recording": app_state.recording_enabled})
#     return jsonify({"status": "voice_changed", "new_voice": voice}), 200

@app.route("/set_voice", methods=["POST"])
def set_voice():
    """Set the assistant's voice only after the previous response is completed."""
    data = request.get_json()
    voice = data.get("voice")
    valid_voices = ["ballad", "echo", "ash", "coral", "sage", "shimmer"]

    if voice not in valid_voices:
        return jsonify({"error": "Invalid voice selection"}), 400

    # Ensure the assistant is not speaking before updating voice
    if app_state.websocket and app_state.recording_enabled:
        logger.warning("Cannot update voice while assistant audio is playing. Please wait.")
        return jsonify({"error": "Cannot change voice while assistant is speaking."}), 400

    # Update voice in app state
    app_state.voice = voice
    logger.info(f"Voice changed to: {voice}")

    # Emit status update to frontend
    socketio.emit("status_update", {"voice": voice, "recording": app_state.recording_enabled}, namespace='/')

    # Send a session update to OpenAI WebSocket
    if app_state.websocket:
        session_update = {
            "type": "session.update",
            "session": {
                "voice": app_state.voice,
            },
        }
        asyncio.run(app_state.websocket.send(json.dumps(session_update)))
        logger.info(f"📨 Sent voice update to OpenAI WebSocket: {voice}")

    return jsonify({"status": "voice_changed", "new_voice": voice}), 200

@app.route('/api/files')
def list_files():
    scratchpad_dir = os.getenv("SCRATCH_PAD_DIR", "./scratchpad")
    path = request.args.get('path', '')
    
    try:
        full_path = os.path.join(scratchpad_dir, path)
        if not os.path.exists(full_path):
            return jsonify({"error": "Path not found"}), 404
            
        files = []
        for entry in os.listdir(full_path):
            entry_path = os.path.join(full_path, entry)
            files.append({
                "name": entry,
                "path": os.path.join(path, entry),
                "isDirectory": os.path.isdir(entry_path)
            })
            
        return jsonify({
            "files": sorted(files, key=lambda x: (not x['isDirectory'], x['name'])),
            "currentDir": path
        })
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({"error": "Server error"}), 500

@app.route('/api/files/content')
def get_file_content():
    scratchpad_dir = os.getenv("SCRATCH_PAD_DIR", "./scratchpad")
    path = request.args.get('path', '')
    
    try:
        full_path = os.path.join(scratchpad_dir, path)
        if not os.path.exists(full_path):
            return jsonify({"error": "File not found"}), 404
            
        if os.path.isdir(full_path):
            return jsonify({"error": "Path is a directory"}), 400
            
        # Only preview text files
        if full_path.endswith(('.txt', '.md', '.log', '.json', '.py', '.js')):
            with open(full_path, 'r') as f:
                content = f.read()
            return Response(content, mimetype='text/plain')
        else:
            return send_file(full_path, as_attachment=False)
            
    except Exception as e:
        logger.error(f"Error retrieving file: {e}")
        return jsonify({"error": "Server error"}), 500


@app.route("/start_recording", methods=["POST"])
def start_recording():
    """Start recording user input."""
    logger.debug("Received request to start recording.")

    if app_state.mic is None:
        logger.info("Initializing microphone.")
        app_state.mic = AsyncMicrophone()

    app_state.mic.start_recording()
    app_state.recording_enabled = True
    logger.info("Recording started.")

    socketio.emit("status_update", {"voice": app_state.voice, "recording": True})
    return jsonify({"status": "recording_started"}), 200

@app.route("/stop_recording", methods=["POST"])
def stop_recording():
    """Stop recording user input."""
    logger.debug("Received request to stop recording.")

    if app_state.mic:
        app_state.mic.stop_recording()
        logger.info("Recording stopped.")
    else:
        logger.warning("Attempted to stop recording, but microphone was not initialized.")

    app_state.recording_enabled = False
    socketio.emit("status_update", {"voice": app_state.voice, "recording": False})
    return jsonify({"status": "recording_stopped"}), 200

@app.route("/status", methods=["GET"])
def get_status():
    """Get the current status of the assistant."""
    logger.debug("Status request received.")
    return jsonify({
        "voice": app_state.voice,
        "recording": app_state.recording_enabled
    }), 200

@socketio.on("connect")
def handle_connect():
    """Send status update when a client connects."""
    logger.info("New WebSocket connection established.")
    socketio.emit("status_update", {"voice": app_state.voice, "recording": app_state.recording_enabled})

# --- WebSocket Handling ---
async def process_message_queue(ws):
    """Processes messages queued for the OpenAI WebSocket."""
    while not app_state.exit_event.is_set():
        try:
            message = await app_state.message_queue.get()
            logger.debug(f"🔼 Sending message to OpenAI WebSocket: {message}")
            await ws.send(message)
        except Exception as e:
            logger.error(f"❌ Error sending message to WebSocket: {e}")

async def realtime_api():
    """Manages real-time interaction with OpenAI's WebSocket API."""
    while not app_state.exit_event.is_set():
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY is missing in the environment.")
                await asyncio.sleep(5)
                continue

            url = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "OpenAI-Beta": "realtime=v1",
            }

            logger.info("Connecting to OpenAI WebSocket API...")
            async with websockets.connect(url, extra_headers=headers) as ws:
                app_state.websocket = ws
                logger.info("✅ Connected to OpenAI WebSocket.")

                session_update = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text", "audio"],
                        "instructions": SESSION_INSTRUCTIONS,
                        "voice": app_state.voice,
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16",
                        "turn_detection": {
                            "type": "server_vad",
                            "threshold": SILENCE_THRESHOLD,
                            "prefix_padding_ms": PREFIX_PADDING_MS,
                            "silence_duration_ms": SILENCE_DURATION_MS,
                        },
                        "tools": TOOL_SCHEMAS,
                    },
                }
                await ws.send(json.dumps(session_update))
                logger.info("📨 Sent session update to OpenAI WebSocket.")

                if app_state.mic is None:
                    logger.info("🎤 Initializing microphone.")
                    app_state.mic = AsyncMicrophone()

                ws_task = asyncio.create_task(process_ws_messages(ws, app_state.mic))
                sender_task = asyncio.create_task(process_message_queue(ws))

                try:
                    while not app_state.exit_event.is_set():
                        if app_state.recording_enabled:
                            audio_data = app_state.mic.get_audio_data()
                            if audio_data:
                                base64_audio = base64_encode_audio(audio_data)
                                if base64_audio:
                                    logger.debug("🎤 Sending recorded audio data to OpenAI WebSocket.")
                                    await ws.send(json.dumps({
                                        "type": "input_audio_buffer.append",
                                        "audio": base64_audio
                                    }))
                        await asyncio.sleep(0.01)
                except Exception as e:
                    logger.error(f"❌ Error in recording loop: {e}")

                sender_task.cancel()
                ws_task.cancel()
                logger.info("Closing WebSocket connection.")
                await ws.close()

        except ConnectionClosedError as e:
            logger.warning(f"⚠️ WebSocket connection closed: {e}")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"❌ Error in realtime API: {e}")
            await asyncio.sleep(1)

def run_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(realtime_api())

if __name__ == "__main__":
    logger.info("🚀 Starting real-time API in background thread.")
    thread = Thread(target=run_asyncio_loop, daemon=True)
    thread.start()

    logger.info("🌐 Starting Flask-SocketIO server.")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
