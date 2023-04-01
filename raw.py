def main():
    # Initialize game variables
    global players
    global round_scores
    global total_scores
    global tables
    global current_round
    global current_table
    global current_player
    global discard_pile
    global extra_deck
    global wild_red_3s
    global wrap_around_runs
    global buying
    global buying_order
    global shanghai

    global num_players, num_rounds, tables_per
    print("Welcome to Rummy!")

    num_players = int(input("Enter the number of players: "))
    while num_players < 3 or num_players > 20:
        num_players = int(input("Invalid number of players. Enter a number between 2 and 22: "))

    num_rounds = 7;

    num_tables = get_num_tables(num_players)
    players_per_table = get_players_per_table(num_players, num_tables, [], 1)

    print("Dealing cards...")
    decks = initialize_decks()
    draw_pile = []
    for deck in decks:
        draw_pile.extend(deck)
    random.shuffle(draw_pile)
    deal_cards(players_per_table, draw_pile)

    print("Initializing discard piles...")
    discard_piles = initialize_discard(num_tables)

    # Start the game loop
    for round_num in range(1, 8):
        current_round = round_num
        round_scores = {}
        total_scores = {}

        # Play the round at each table
        for table in tables:
            current_table = table
            # Initialize variables for the table
            table_scores = {}
            players_at_table = table["players"]
            shanghai_declared = False
            # Set up the deck and deal hands
            deck = create_deck(extra_deck)
            hands = deal_hands(players_at_table, deck)
            discard_pile = [draw_card(deck)]
            # Play the round
            for i in range(len(players_at_table)):
                current_player = players_at_table[i]
                # Allow player to complete their turn
                take_turn(current_player, hands[current_player], deck)
                # Check for shanghai and declare if necessary
                if shanghai_check(discard_pile[-1], hands[current_player]):
                    shanghai_declared = True
                    shanghai[current_round][table["num"]] = current_player
                    break
            # Score the round
            for player in players_at_table:
                table_scores[player] = score_hand(hands[player])
                if shanghai_declared:
                    table_scores[player] += 50
            round_scores[table["num"]] = table_scores
        # Add round scores to total scores
        for player in players:
            total_scores[player].append(sum([round_scores[table_num][player] for table_num in range(len(tables))]))
        # Sort and display scores
        sorted_scores = sorted(total_scores.items(), key=lambda x: x[1])
        print(f"Scores after round {round_num}:")
        for i in range(len(sorted_scores)):
            print(f"{i+1}. {sorted_scores[i][0]}: {sorted_scores[i][1][-1]}")
        # Reassign players to tables for next round
        tables = assign_tables_and_seats(sorted_scores)

    # Determine winner(s)
    sorted_scores = sorted(total_scores.items(), key=lambda x: x[1])
    winners = []
    for i in range(len(sorted_scores)):
        if sorted_scores[i][1][-1] == sorted_scores[0][1][-1]:
            winners.append(sorted_scores[i][0])
        else:
            break
    if len(winners) == 1:
        print(f"{winners[0]} wins!")
    else:
        print("Tie between:")
        for winner in winners:
            print(winner)

def take_turn(player, table, deck, extra_deck, wild_red_3s, wrap_around_runs, buying, buying_order, shanghai):
    """
    Perform a player's turn, following the rules of the game.

    Args:
    - player: the player taking the turn
    - table: the table the player is seated at
    - deck: the main deck of cards
    - extra_deck: the extra deck of cards
    - wild_red_3s: whether red 3s are wild
    - wrap_around_runs: whether runs can wrap around
    - buying: the buying variable
    - buying_order: the buying order variable
    - shanghai: the shanghai variable

    Returns:
    - None
    """
    # Draw a card from the deck or the extra deck, if possible
    draw(player, table, deck, extra_deck)

    # Check if any sets or runs can be laid down
    laydown(player, table, wrap_around_runs)

    # Check if any cards can be played on existing sets or runs
    play(player, table, wild_red_3s, wrap_around_runs)

    # Discard a card, if necessary
    discard(player, table, buying, buying_order, shanghai)

    # Allow the player to buy a card, if necessary
    buying(player, table, buying, buying_order, shanghai, deck, extra_deck)

def draw(player, draw_pile, discard_pile):
    """
    Draw a card from either the draw pile or the discard pile, depending on player's choice.
    Return the drawn card and the updated draw and discard piles.
    """
    while True:
        choice = input(f"{player.name}, do you want to draw a card from the draw pile (1) or the discard pile (2)? ")
        if choice == "1":
            drawn_card = draw_pile.pop()
            break
        elif choice == "2":
            if len(discard_pile) == 0:
                print("The discard pile is empty. You must draw from the draw pile.")
            else:
                drawn_card = discard_pile.pop()
                break
        else:
            print("Invalid choice. Please enter 1 to draw from the draw pile or 2 to draw from the discard pile.")
    
    return drawn_card, draw_pile, discard_pile

def draw(player, draw_pile, discard_pile):
    """
    Draw a card from either the draw pile or the discard pile, depending on player's choice.
    Return the drawn card and the updated draw and discard piles.
    """
    while True:
        choice = input(f"{player.name}, do you want to draw a card from the draw pile (1) or the discard pile (2)? ")
        if choice == "1":
            drawn_card = draw_pile.pop()
            break
        elif choice == "2":
            if len(discard_pile) == 0:
                print("The discard pile is empty. You must draw from the draw pile.")
            else:
                drawn_card = discard_pile.pop()
                break
        else:
            print("Invalid choice. Please enter 1 to draw from the draw pile or 2 to draw from the discard pile.")
    
    return drawn_card, draw_pile, discard_pile

def get_round_objective(round_num):
    """Return the objective for a given round number."""
    objectives = {
        1: (2, 'sets'),
        2: (1, 'set', 1, 'run'),
        3: (2, 'runs'),
        4: (3, 'sets'),
        5: (2, 'sets', 1, 'run'),
        6: (1, 'set', 2, 'runs'),
        7: (3, 'runs')
    }
    return objectives.get(round_num)

def is_set(cards):
    """Check if a list of cards forms a set."""
    ranks = [card.rank for card in cards]
    return len(set(ranks)) == 1

def is_run(cards, wrap_around=False):
    """Check if a list of cards forms a run."""
    suits = [card.suit for card in cards]
    ranks = [card.rank for card in cards]
    unique_ranks = sorted(set(ranks))
    if wrap_around:
        if len(unique_ranks) < 4:
            return False
        if unique_ranks[-1] == 14 and unique_ranks[0] == 2:
            unique_ranks = [1] + unique_ranks[:-1]
    if len(unique_ranks) < 4:
        return False
    for i in range(len(unique_ranks) - 3):
        if unique_ranks[i:i+4] == list(range(unique_ranks[i], unique_ranks[i]+4)):
            indices = [j for j in range(len(ranks)) if ranks[j] == unique_ranks[i]]
            if all(suits[j] == suits[indices[0]] for j in indices):
                return True
    return False

def lay_down(player, round_num, wrap_around=False):
    """
    Allows the player to lay down cards from their hand that satisfy the round's objective.

    Args:
        player: The active player.
        round_num: The current round number.
        wrap_around: Whether to allow wrap-around runs.

    Returns:
        A tuple of the cards laid down, if any, and a boolean indicating whether the player has completed the round's objective.
    """
    cards_laid_down = []
    objective_complete = False

    # Get the round objective
    objective = get_round_objective(round_num)

    # Check if the player has already laid down cards for this round
    if objective in player.laid_down:
        print("You have already laid down cards for this round.")
        return [], objective_complete

    # Get the cards in the player's hand that match the objective
    valid_cards = []
    if objective.count('sets') > 0:
        sets = [cards for cards in player.hand if is_set(cards)]
        valid_cards.extend(sets * objective.count('sets'))
    if objective.count('runs') > 0:
        runs = [cards for cards in player.hand if is_run(cards, wrap_around)]
        valid_cards.extend(runs * objective.count('runs'))

    # If the player has valid cards, ask them which ones they want to lay down
    if valid_cards:
        print("You have the following cards that match the objective:")
        for i, cards in enumerate(valid_cards):
            print(f"{i + 1}: {cards}")
        print("Which cards would you like to lay down? (Enter card numbers separated by commas, or 'none')")
        lay_down_input = input().strip().lower()

        if lay_down_input != "none":
            # Parse the input and get the cards to lay down
            card_nums = [int(num) - 1 for num in lay_down_input.split(",")]
            cards_to_lay_down = [valid_cards[i] for i in card_nums]

            # Check that the selected cards form a valid set/run and satisfy the round objective
            if is_valid_lay_down(cards_to_lay_down, objective, wrap_around):
                cards_laid_down = cards_to_lay_down
                objective_complete = is_objective_complete(player, objective)
                print("Cards laid down successfully!")
            else:
                print("Those cards do not form a valid set/run or do not satisfy the round objective.")
        else:
            print("No cards laid down.")
    else:
        print("You do not have any cards that match the objective.")

    return cards_laid_down, objective_complete

def is_valid_lay_down(cards_laid_down, round_obj, wrap_around=False):
    """
    Check if the cards laid down form a valid set/run and satisfy the round objective.

    Args:
        cards_laid_down: The cards laid down by the player.
        round_obj: The objective for the current round.
        wrap_around: Whether to allow wrap-around runs.

    Returns:
        A boolean indicating whether the cards laid down form a valid set/run and satisfy the round objective.
    """
    if round_obj is None:
        return False

    # Check that the cards laid down form a valid set/run
    if round_obj[0] == 1:
        if not is_set(cards_laid_down):
            return False
    elif round_obj[0] == 2:
        if not is_run(cards_laid_down, wrap_around):
            return False
    elif round_obj[0] == 3:
        if not (is_set(cards_laid_down[:3]) and is_run(cards_laid_down[3:], wrap_around)):
            return False

    # Check that the cards laid down satisfy the round objective
    objective_counts = {}
    for card in cards_laid_down:
        if card.rank in objective_counts:
            objective_counts[card.rank] += 1
        else:
            objective_counts[card.rank] = 1

    for i in range(0, len(round_obj), 2):
        count = round_obj[i]
        type_ = round_obj[i+1]
        if type_ == "set":
            if count not in objective_counts.values():
                return False
        elif type_ == "run":
            ranks = sorted(list(objective_counts.keys()))
            for j in range(len(ranks) - count + 1):
                if ranks[j:j+count] == list(range(ranks[j], ranks[j]+count)):
                    break
            else:
                return False

    return True

def play(active_player, table):
    """
    Allows the active player to play cards to complete a set/run or to add to another player's set/run. 
    Cards played must not invalidate any sets/runs or the current round's objective.
    """
    cards_played = []
    while True:
        card = input(f"{active_player.name}, enter a card to play or type 'done' to end your turn: ")
        if card.lower() == "done":
            break
        card = active_player.hand.pop(int(card)-1)
        if not is_valid_play(card, active_player, table):
            active_player.hand.append(card)
            print("Invalid play! Please try again.")
        else:
            cards_played.append(card)
            print(f"{card} played!")
    # check if any sets/runs are completed with the cards played
    if check_sets_runs(active_player, table, cards_played):
        print(f"{active_player.name} has completed a set/run!")
    else:
        print("No sets/runs completed.")
    return cards_played

def discard(player):
    """
    Allows the active player to discard a card and end their turn.
    """
    global shanghai
    global num_tables
    global tables_finished_round
    current_table = player.table
    current_table.discard_pile.append(player.hand.pop())
    shanghai_check_result = shanghai_check(player, current_table.players)
    if shanghai_check_result:
        for p in current_table.players:
            if p != player:
                p.score += 50
        print("Shanghai!")
    current_table.turn_index += 1
    if current_table.turn_index == current_table.num_players:
        current_table.end_of_round_trigger = True
        tables_finished_round += 1
        if tables_finished_round == num_tables:
            scoring()
            tables_finished_round = 0
    elif current_table.turn_index == (current_table.dealer_index + 1) % current_table.num_players:
        current_table.buying_window_open = True
        if current_table.buy_order == 'play order':
            eligible_players = [p for p in current_table.players if p.eligible_to_buy()]
            num_eligible_players = len(eligible_players)
            if num_eligible_players > 0:
                current_table.buying_window_timer = Timer(10, start_buying, args=(current_table,))
                current_table.buying_window_timer.start()
            else:
                current_table.buying_window_open = False
    else:
        draw(player, 1)

def buying(current_table, active_player=None):
    """
    Determines which players are eligible to buy and allows them to opt in or out of buying the top card from the discard pile.
    If no player buys the card, it is added to the bottom of the draw pile.
    """
    global discard_pile, draw_pile, buy_order

    # Determine which players are eligible to buy
    restricted_players = [current_table.turn_index, (current_table.turn_index + 1) % current_table.num_players]
    eligible_players = [p for p in current_table.players if p.index not in restricted_players]

    # Wait for eligible players to opt in to buying (if buy order is set to play order)
    if current_table.buy_order == 'play order':
        for player in eligible_players:
            if player == active_player:
                continue
            print(f"{player.name}, do you want to buy the discard? You have 10 seconds to decide.")
            buy_choice = input()
            if buy_choice.lower() == 'buy':
                current_table.buying_player = player
                break
        else:
            return

    # Determine the card to be bought
    bought_card = discard_pile[-1]
    print(f"The card to be bought is {bought_card}.")

    # Determine the order in which eligible players will buy the card
    if current_table.buy_order == 'first come':
        current_table.buy_order = eligible_players
    elif current_table.buy_order == 'play order':
        current_table.buy_order = sorted(eligible_players, key=lambda x: (x.index - current_table.turn_index) % current_table.num_players)

    # Iterate through eligible players in buy order
    for player in current_table.buy_order:
        if current_table.buying == 'strict' or player == current_table.buying_player:
            # Player must buy the card
            print(f"{player.name}, you must buy the card.")
            player.hand.append(discard_pile.pop())
            player.hand.append(draw_pile.pop(0))
            break
        else:
            # Player may opt out of buying the card
            print(f"{player.name}, do you want to buy the discard? Type 'buy' to buy or anything else to pass.")
            buy_choice = input()
            if buy_choice.lower() == 'buy':
                player.hand.append(discard_pile.pop())
                player.hand.append(draw_pile.pop(0))
                break
            else:
                continue

    # If no player buys the card, add it to the bottom of the draw pile
    else:
        draw_pile.append(discard_pile.pop())

def start_buying(table):
    global turn, discard_pile, draw_pile, buying, buy_order

    print("Buying window open!")
    print(f"Discard pile: {discard_pile[-1]}")

    # Determine which players are eligible to buy
    restricted_players = [table.turn_index, (table.turn_index + 1) % table.num_players]
    eligible_players = [(i + 2) % table.num_players for i in range(table.num_players) if i not in restricted_players]

    # Wait for eligible players to opt in to buying (if buy order is set to play order)
    if table.buy_order == 'play order':
        for player in eligible_players:
            print(f"Player {player + 1}, do you want to buy the discard? You have 10 seconds to decide.")
            buy_choice = input()
            if buy_choice.lower() == 'buy':
                active_player = player
                break
        else:
            table.buying_window_open = False
            return

    # Determine the card to be bought
    bought_card = discard_pile[-1]
    print(f"The card to be bought is {bought_card}.")

    # Determine the order in which eligible players will buy the card
    if table.buy_order == 'first come':
        buy_order = eligible_players
    elif table.buy_order == 'play order':
        buy_order = sorted(eligible_players, key=lambda x: (x - table.turn_index) % table.num_players)

    # Iterate through eligible players in buy order
    for player in buy_order:
        if buying == 'strict' or player == active_player:
            # Player must buy the card
            print(f"Player {player + 1}, you must buy the card.")
            player_hand[player].append(discard_pile.pop())
            player_hand[player].append(draw_pile.pop(0))
            break
        else:
            # Player may opt out of buying the card
            print(f"Player {player + 1}, do you want to buy the discard? Type 'buy' to buy or anything else to pass.")
            buy_choice = input()
            if buy_choice.lower() == 'buy':
                player_hand[player].append(discard_pile.pop())
                player_hand[player].append(draw_pile.pop(0))
                break
            else:
                continue

    # If no player buys the card, add it to the bottom of the draw pile
    else:
        draw_pile.append(discard_pile.pop())

    table.buying_window_open = False
    table.turn_index += 1
    if table.turn_index == table.num_players:
        table.end_of_round_trigger = True
    elif table.turn_index == (table.dealer_index + 1) % table.num_players:
        table.buying_window_open = True
        if table.buy_order == 'play order':
            eligible_players = [p for p in table.players if p.eligible_to_buy()]
            num_eligible_players = len(eligible_players)
            if num_eligible_players > 0:
                table.buying_window_timer = Timer(10, start_buying, args=(table,))
                table.buying_window_timer.start()
            else:
                table.buying_window_open = False
    else:
        draw(table.players[table.turn_index])

def scoring(round_scores, table_scores, shanghais, hands, wild_red_3s):
    round_scores.append({})
    for i in range(len(hands)):
        score = 0
        for card in hands[i]:
            if card == "R3" and wild_red_3s:
                continue
            elif card in ["D3", "H3"]:
                score += 20 if wild_red_3s else 3
            elif card[0] in ['J', 'Q', 'K']:
                score += 10
            elif card[0] == 'A':
                score += 15
            elif card[1:] == '10':
                score += 10
            else:
                score += int(card[1:])
        if i in table_scores:
            if shanghais[table_scores.index(i)]:
                score += 50
        round_scores[-1][i] = score
    return round_scores, table_scores, shanghais

def sort_hand(hand):
    print("Current hand: ", hand)
    start = int(input("Enter the index of the starting card to sort (0-9): "))
    end = int(input("Enter the index of the ending card to sort (0-9): "))

    # Validate the inputs
    while not (0 <= start <= 9 and start <= end <= 9):
        print("Invalid input! Please try again.")
        start = int(input("Enter the index of the starting card to sort (0-9): "))
        end = int(input("Enter the index of the ending card to sort (0-9): "))

    print("Sort by:")
    print("1. Rank")
    print("2. Suit")
    choice = int(input("Enter your choice (1-2): "))

    # Validate the input
    while choice not in (1, 2):
        print("Invalid input! Please try again.")
        choice = int(input("Enter your choice (1-2): "))

    if choice == 1:
        # Sort by rank
        hand[start:end+1] = sorted(hand[start:end+1], key=lambda x: x[0])
    else:
        # Sort by suit
        hand[start:end+1] = sorted(hand[start:end+1], key=lambda x: x[1])

    print("Sorted hand: ", hand)
  
def get_num_tables(num_players):
    if num_players < 8:
        return 1
    elif num_players < 13:
        return 2
    elif num_players < 18:
        return 3
    else:
        return 4