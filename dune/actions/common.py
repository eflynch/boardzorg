
from dune.exceptions import IllegalAction, BadCommand

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


def spend_spice(game_state, faction, amount, context=None):
    spice_to_spend = game_state.faction_state[faction].spice
    if game_state.spice_context[faction] is not None:
        if game_state.spice_reserve[faction] is not None:
            if context == game_state.spice_context[faction]:
                game_state.spice_reserve[faction] = None
                game_state.spice_context[faction] = None
            else:
                spice_to_spend = game_state.faction_state[faction].spice - game_state.spice_reserve[faction]
    if amount > spice_to_spend:
        raise BadCommand("Insufficient spice for this action")
    game_state.faction_state[faction].spice -= amount


def check_no_allies(game_state, faction, space):
    for ally in game_state.alliances[faction]:
        if ally in space.forces:
            if ally != "bene-gesserit":
                raise BadCommand("You cannot invade your ally")
            elif not space.coexist:
                raise BadCommand("You cannot invade your ally")
