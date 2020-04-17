
TOKEN_SECTORS = [1, 4, 7, 10, 13, 16]


def get_faction_order(game_state):
    faction_order = []
    storm_position = game_state.storm_position
    for i in range(18):
        sector = (storm_position + i + 1) % 18
        if sector in TOKEN_SECTORS:
            for f in game_state.faction_state:
                faction_state = game_state.faction_state[f]
                if faction_state.token_position == sector:
                    faction_order.append(f)
    return faction_order