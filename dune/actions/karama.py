from dune.state.treachery_cards import WORTHLESS

# For now, always use a worthless card before a karama card
def discard_karama(game_state, faction):
    t_deck = game_state.faction_state[faction].treachery
    k_card = "Karama"
    if faction == "bene-gesserit":
        worthless = [card for card in t_deck if card in WORTHLESS]
        if worthless:
            k_card = worthless[0]

    t_deck.remove(k_card)
    game_state.treachery_discard.insert(0, k_card)
