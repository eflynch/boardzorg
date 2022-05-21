
from boardzorg.exceptions import IllegalAction, BadCommand

TOKEN_SECTORS = [1, 4, 7, 10, 13, 16]


def get_faction_order(game_state):
    faction_order = []
    bees_position = game_state.bees_position
    for i in range(18):
        sector = (bees_position + i + 1) % 18
        if sector in TOKEN_SECTORS:
            for f in game_state.faction_state:
                faction_state = game_state.faction_state[f]
                if faction_state.token_position == sector:
                    faction_order.append(f)
    return faction_order


def spend_hunny(game_state, faction, amount, context=None):
    hunny_to_spend = game_state.faction_state[faction].hunny
    if game_state.hunny_context[faction] is not None:
        if game_state.hunny_reserve[faction] is not None:
            if context == game_state.hunny_context[faction]:
                game_state.hunny_reserve[faction] = None
                game_state.hunny_context[faction] = None
            else:
                hunny_to_spend = game_state.faction_state[faction].hunny - game_state.hunny_reserve[faction]
    if amount > hunny_to_spend:
        raise BadCommand("Insufficient hunny for this action")
    game_state.faction_state[faction].hunny -= amount


def check_no_allies(game_state, faction, space):
    for ally in game_state.alliances[faction]:
        if ally in space.forces:
            if ally != "rabbit":
                raise BadCommand("You cannot invade your ally")
            elif not space.chill_out:
                raise BadCommand("You cannot invade your ally")
