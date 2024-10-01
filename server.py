import asyncio
import websockets
import random

# Constants
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
}

clients = {}
games = {}

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"

class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        self.value += VALUES[card.rank]
        if card.rank == 'Ace':
            self.aces += 1
        self.adjust_for_ace()

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

async def register(websocket, name):
    clients[websocket] = name
    if name not in games:
        games[name] = {'hand': Hand(), 'score': 0}

async def unregister(websocket):
    if websocket in clients:
        del clients[websocket]
        del games[clients[websocket]]

async def send_scores():
    for websocket in clients.keys():
        name = clients[websocket]
        hand = games[name]['hand']
        await websocket.send(f"{name}'s Hand: {[str(card) for card in hand.cards]} (Value: {hand.value})")

async def play_blackjack(websocket, path):
    name = await websocket.recv()
    await register(websocket, name)
    
    deck = Deck()
    dealer_hand = Hand()
    
    # Initial dealing
    for _ in range(2):
        games[name]['hand'].add_card(deck.deal_card())
        dealer_hand.add_card(deck.deal_card())
    
    await send_scores()

    # Player's turn
    while True:
        action = await websocket.recv()
        if action == 'h':
            games[name]['hand'].add_card(deck.deal_card())
            await send_scores()
            if games[name]['hand'].value > 21:
                await websocket.send(f"{name}, you bust! Dealer wins.")
                break
        elif action == 's':
            break

    # Dealer's turn
    while dealer_hand.value < 17:
        dealer_hand.add_card(deck.deal_card())

    await websocket.send(f"Dealer's Hand: {[str(card) for card in dealer_hand.cards]} (Value: {dealer_hand.value})")
    
    # Determine winner
    player_hand_value = games[name]['hand'].value
    if player_hand_value > 21:
        result = "Dealer wins!"
    elif dealer_hand.value > 21 or player_hand_value > dealer_hand.value:
        result = "You win!"
    elif player_hand_value < dealer_hand.value:
        result = "Dealer wins!"
    else:
        result = "It's a tie!"
    
    await websocket.send(result)
    
    await unregister(websocket)

async def main():
    async with websockets.serve(play_blackjack, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

