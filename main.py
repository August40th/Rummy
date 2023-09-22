from collections import deque
import random

# Initialize the cards
suits = ['H', 'D', 'C', 'S']
ranks = [str(rank) for rank in range(1, 14)]  # Convert ranks to strings
deck = [(rank, suit) for rank in ranks for suit in suits]

# Function to create the draw pile
def create_draw_pile(num_decks):
    draw_pile = deck * num_decks
    random.shuffle(draw_pile)
    random.shuffle(draw_pile)
    return draw_pile

# Initialize and shuffle the draw pile
num_decks = 2
draw_pile = create_draw_pile(num_decks)

# Initialize the discard pile
discard_pile = []

# Function to repopulate the draw pile with the shuffled discard pile (minus the top five cards)
def reshuffle(draw_pile, discard_pile):
    top_five = discard_pile[:5]
    remaining_cards = discard_pile[5:]
    draw_pile.extend(remaining_cards)
    random.shuffle(draw_pile)
    return top_five

class Round_Objective:
    def __init__(self):
        self.round = 0

    def get_objective(self):
        sets, runs = 0, 0

        if self.round == 1:
            sets, runs = 2, 0
        elif self.round == 2:
            sets, runs = 1, 1
        elif self.round == 3:
            sets, runs = 0, 2
        elif self.round == 4:
            sets, runs = 3, 0
        elif self.round == 5:
            sets, runs = 2, 1
        elif self.round == 6:
            sets, runs = 1, 2
        elif self.round == 7:
            sets, runs = 0, 3

        return sets, runs

    def next_round(self):
        self.round += 1
        players.rotate(-1)

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.buys = 0
        self.laid_down = False
        self.cumulative_score = 0
        
    def deal_card(self):
        if draw_pile:
            drawn_card = draw_pile.pop()
            self.hand.append(drawn_card)
    
    def draw_card(self, draw_pile, discard_pile):
        print("\n" + self.name + "'s turn to draw") 
        self.hand.sort(key=lambda card: ranks.index(card[0]), reverse=True)
        print(self.name, "'s Hand:", [f"{rank}{suit}" for rank, suit in self.hand])
    
        drawn_card = None
        cards_match = []
    
        if discard_pile:
            top_card = discard_pile[-1]
            cards_match = [card for card in self.hand if card[0] == top_card[0]]
        else:
            top_card = None
    
        if self.laid_down and discard_pile:
            for other_player in players:
                for card in other_player.hand:
                    if card[0] == top_card[0]:
                        drawn_card = discard_pile.pop()
                        self.hand.append(drawn_card)
                        print(self.name + " drew", f"{drawn_card[0]}{drawn_card[1]}", "from the discard pile to play in the set")
                        return
    
            if top_card and ranks.index(top_card[0]) > ranks.index(self.hand[-1][0]):
                drawn_card = discard_pile.pop()
                self.hand.append(drawn_card)
                print(self.name + " drew", f"{drawn_card[0]}{drawn_card[1]}", "from the discard pile because it's lower")
    
        elif not self.laid_down and discard_pile:
            if len(cards_match) >= 2:
                cards_match.clear()
                drawn_card = discard_pile.pop()
                self.hand.append(drawn_card)
                print(self.name + " drew", f"{drawn_card[0]}{drawn_card[1]}", "from the discard pile because of a matching pair for a set")
    
        if not drawn_card:
            drawn_card = draw_pile.pop()
            self.hand.append(drawn_card)
            print(self.name + " drew", f"{drawn_card[0]}{drawn_card[1]}", "from the deck")
    
        cards_match.clear()
        
    def discard_card(self, discard_pile):
        discard_choice = None
        pairs = []
        sets = []
        potential_discard = []
    
        if self.laid_down:
            self.hand.sort(key=lambda card: ranks.index(card[0]))
            rank_cards = [card for card in self.hand]
            potential_discard.append(rank_cards)
        else:
            for rank in reversed(ranks):  # Reverse to prioritize high-ranking cards
                self.hand.sort(key=lambda card: ranks.index(card[0]))
                rank_cards = [card for card in self.hand if card[0].startswith(rank)]
                if len(rank_cards) == 1:
                    potential_discard.append(rank_cards)
            if not potential_discard:
                for rank in reversed(ranks):
                    rank_cards = [card for card in self.hand if card[0].startswith(rank)]
                    if len(rank_cards) == 4 or len(rank_cards) == 5:
                        potential_discard.append(rank_cards)
            if not potential_discard:
                for rank in reversed(ranks):
                    rank_cards = [card for card in self.hand if card[0].startswith(rank)]
                    if len(rank_cards) == 2:
                        potential_discard.append(rank_cards)
            if not potential_discard:
                for rank in reversed(ranks):
                    rank_cards = [card for card in self.hand if card[0].startswith(rank)]
                    if len(rank_cards) == 3:
                        potential_discard.append(rank_cards)
    
        last_check = potential_discard
    
        if len(potential_discard) == 0 and len(self.hand) > 1:
            potential_discard = last_check
            discard_choice = self.hand[-1]
        else:
            discard_choice = potential_discard[0][0]
    
        # Remove the card from the player's hand and discard it
        if len(self.hand) > 1:
            self.hand.remove(discard_choice)
            discard_pile.append(discard_choice)
            print(self.name + " discarded", f"{discard_choice[0]}{discard_choice[1]}")
        else:
            for card in self.hand:
                discard_pile.append(card)
                self.hand.remove(card)
                print(self.name + " discarded", f"{card[0]}{card[1]}")
                
    def buy_from_discard(self, discard_pile, draw_pile):
        if self.buys < 3:
            if discard_pile:
                card_from_discard = discard_pile.pop()
                self.hand.append(card_from_discard)
            if draw_pile:
                card_from_draw = draw_pile.pop()
                self.hand.append(card_from_draw)
            self.buys += 1
            
def score_hand(hand):
    score = 0
    for card in hand:
        rank, suit = card  # Unpack the card tuple
        if rank == '3' and suit in ['D', 'H']:  # Red 3's
            score += 20
        elif '2' <= rank <= '9':
            score += int(rank)
        elif rank == '1':  # Ace
            score += 15
        elif rank in ['10', '11', '12', '13']:  # 10, Jack, Queen, King
            score += 10
    return score
    
# Create four computer players
alice = Player("Alice")
bob = Player("Bob")
charlie = Player("Charlie")
dawn = Player("Dawn")
players = deque([alice, bob, charlie, dawn])

# Initialize the Round Objective class
objective = Round_Objective()

for round_number in range(1, 7):
    print(f"\n--- Round {round_number} ---")

    # Set up the required collections for the current round
    objective.round = round_number
    round_sets, round_runs = objective.get_objective()
    print(f"Required Sets: {round_sets}, Required Runs: {round_runs}")
    
    # Display the draw pile
    draw_pile_formatted = [f"{rank}{suit}" for rank, suit in reversed(draw_pile)]
    print("Draw pile: ", draw_pile_formatted)
    
    # Shuffle the draw pile and distribute 10 cards to each player
    c = 1
    while c < 11:
        for player in players:
            player.deal_card()
        c += 1

    # Display each player's initial hand
    for player in players:
        player.hand = sorted(player.hand, key=lambda card: (card[1], card[0]))
        sorted_hand = [f"{rank}{suit}" for rank, suit in player.hand]  # Format cards as rank and suit without space
        print(f"{player.name}'s Hand: {sorted_hand}")
        player.draw_card(draw_pile, discard_pile)
        player.hand = sorted(player.hand, key=lambda card: (card[1], card[0]))
        sorted_hand = [f"{rank}{suit}" for rank, suit in player.hand]  # Format cards as rank and suit without space
        print(f"{player.name}'s Hand: {sorted_hand}")
        player.discard_card(discard_pile)

    # End round
    for player in players:
        player.cumulative_score += score_hand(player.hand)
        print(f"{player.name}'s Score: {player.cumulative_score}")
        player.hand = []
    draw_pile = create_draw_pile(num_decks)
    discard_pile = []
    objective.next_round()
