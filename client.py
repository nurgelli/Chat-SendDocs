import asyncio
import websockets

async def send_message(websocket, username):

    try:
        while True:
            message = await asyncio.to_thread(input)
            
            full_message = f"{username.upper()}: {message}"
            await websocket.send(full_message)
            
    except (EOFError, KeyboardInterrupt):
        return

async def receive_messages(websocket):

    try:
        while True:
            message = await websocket.recv()
            print(f"{message}")
    except websockets.exceptions.ConnectionClosed:
        print(f"\nClient exiting...")


async def main():


    print("Enter server IP (default: localhost): ")
    server_ip = await asyncio.to_thread(input)
    if not server_ip:
        server_ip = "localhost"
    
    SERVER_URI = f"ws://{server_ip}:8000"
    
    print("Enter name: ")
    username = await asyncio.to_thread(input)
    if not username:
        username = "unknown"
        
    try:
        async with websockets.connect(SERVER_URI) as websocket:
            print(f"Connected to server")
            print("Ctr+C to exit")
            print("Type something...")
            
            send_task = asyncio.create_task(send_message(websocket, username))
            receive_task = asyncio.create_task(receive_messages(websocket))
            
            done, pending = await asyncio.wait([send_task, receive_task],return_when=asyncio.FIRST_COMPLETED,)
            
            for task in pending:
                task.cancel()
    except ConnectionError:
        print("Cant connet to server")
   

if __name__ == "__main__":
    asyncio.run(main())
