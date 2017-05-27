from actions.shipment import Shipment
from actions.spice import ChoamCharity, Gift, Bribe
from actions.storm import Storm


def get_supervisor_action(game_state):
    round_state = game_state.round_stat
    if round_state.round == "setup":
        if round_state.fremen_placed and round_state.bene_gesserit_placed:
            return Storm()


def get_valid_actions(game_state, faction):
    return {
        "shipment": Shipment,
        "choam_charity": ChoamCharity,
        "gift": Gift,
        "bribe": Bribe,
        "storm": Storm
    }
