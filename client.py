import asyncio
import websockets

async def play_blackjack():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        name = input("What's your name? ")
        await websocket.send(name)  
        
        while True:
            response = await websocket.recv()
            print(response)
            if "bust" in response or "win" in response or "tie" in response:
                break
            
            action = input("Do you want to (h)it or (s)tand? ").lower()
            await websocket.send(action)  

if __name__ == '__main__':
    asyncio.run(play_blackjack())

