import time
from collections import defaultdict

GLOBAL_ROOMS = defaultdict(list)

def get_room_messages(room_id: str):
    return GLOBAL_ROOMS[room_id]

def send_room_message(room_id: str, sender: str, text: str):
    if not text.strip():
        return
    msg = {
        "sender": sender,
        "text": text,
        "time": time.strftime("%H:%M:%S")
    }
    GLOBAL_ROOMS[room_id].append(msg)
    if len(GLOBAL_ROOMS[room_id]) > 50:
        GLOBAL_ROOMS[room_id].pop(0)