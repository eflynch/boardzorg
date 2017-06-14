
from dune.session import Session
from dune.exceptions import IllegalAction, BadCommand

import random
import json
import logging

logger = logging.getLogger(__name__)


def translate_faction(faction):
    return {
        "b": "bene-gesserit",
        "a": "atreides",
        "f": "fremen",
        "h": "harkonnen",
        "e": "emperor",
        "g": "guild"
    }[faction]


def run_game(cmds):
    session = Session()

    for faction, cmd in cmds:
        logger.debug(list(session.get_valid_actions(translate_faction(faction)).keys()))
        try:
            session.handle_cmd(translate_faction(faction), cmd)
        except IllegalAction as e:
            logger.error("    IllegalAction: {}".format(e))
        except BadCommand as e:
            logger.error("    BadComand: {}".format(e))

    final_state = session.game_log[-1]

    # print(json.dumps(final_state.visible("fremen"), indent=4))


CMDS = [
    ("b", "predict harkonnen 5"),
    ("b", "place-token 1"),
    ("a", "place-token 4"),
    ("e", "place-token 7"),
    ("f", "place-token 10"),
    ("g", "place-token 13"),
    ("h", "place-token 16"),
    ("b", "select-traitor Piter-DeVries"),
    ("a", "select-traitor Stilgar"),
    ("f", "select-traitor Gurney-Halleck"),
    ("g", "select-traitor Jamis"),
    ("e", "select-traitor Chani"),
    ("f", "fremen-placement tabr:1,1,2 west:16:1,1,1 south:3:1,1,1,1"),
    ("b", "bene-gesserit-placement Polar-Sink -1"),
    ("f", "bid 1"),
    ("b", "choam-charity"),
    ("g", "bid 2"),
    ("h", "bid 3"),
    ("b", "pass"),
    ("a", "bid 4"),
    ("e", "pass"),
    ("f", "pass"),
    ("g", "pass"),
    ("h", "bid 5"),
    ("a", "pass"),
    ("h", "pay-bid"),
    ("a", "karama-pass-stop-extra"),
    ("b", "karama-pass-stop-extra"),
    ("e", "karama-pass-stop-extra"),
    ("f", "karama-pass-stop-extra"),
    ("g", "karama-pass-stop-extra"),
    ("g", "bid 1"),
    ("h", "pass"),
    ("b", "pass"),
    ("a", "pass"),
    ("e", "pass"),
    ("f", "pass"),
    ("g", "pay-bid"),
    ("h", "bid 1"),
    ("b", "pass"),
    ("a", "pass"),
    ("e", "pass"),
    ("f", "pass"),
    ("g", "pass"),
    ("h", "pay-bid"),
    ("g", "karama-stop-extra"),
    ("b", "pass"),
    ("a", "pass"),
    ("e", "pass"),
    ("f", "pass"),
    ("g", "pass"),
    ("h", "pass"),
    ("b", "karama-pass-block-guild-turn-choice"),
    ("a", "karama-pass-block-guild-turn-choice"),
    ("f", "karama-pass-block-guild-turn-choice"),
    ("e", "karama-pass-block-guild-turn-choice"),
    ("h", "karama-pass-block-guild-turn-choice"),
    ("b", "coexist-persist"),
    ("g", "guild-pass-turn"),
    ("f", "end-movement"),
    ("g", "guild-pass-turn"),
    ("h", "ship 1,1,1,1 Arrakeen 9"),
    ("g", "karama-pass-stop-shipment"),
    ("h", "pay-shipment"),
    ("b", "send-spiritual-advisor"),
    ("h", "karama-pass-stop-spiritual-advisor"),
    ("h", "move 1,1,1,1 Arrakeen 9 Imperial-Basin 9"),
    ("g", "guild-pass-turn"),
    ("b", "ship 1 Sietch-Tabr 13"),
    ("g", "karama-pass-stop-shipment"),
    ("b", "pay-shipment"),
    ("b", "end-movement"),
    ("g", "guild-pass-turn"),
    ("a", "end-movement"),
    ("g", "guild-pass-turn"),
    ("e", "end-movement"),
    ("g", "cross-ship 1,1,1 Tueks-Sietch 4 Carthag 10"),
    ("g", "move 1,1 Tueks-Sietch 4 Pasty-Mesa 6"),
    ("b", "voice no poison weapon"),
    ("a", "karama-pass-voice"),
    ("f", "karama-pass-voice"),
    ("e", "karama-pass-voice"),
    ("h", "karama-pass-voice"),
    ("g", "karama-pass-voice"),
    ("a", "karama-pass-fedaykin"),
    ("b", "karama-pass-fedaykin"),
    ("e", "karama-pass-fedaykin"),
    ("h", "karama-pass-fedaykin"),
    ("g", "karama-pass-fedaykin"),
    ("b", "commit-plan Alia 1 - -"),
    ("f", "commit-plan Stilgar 1 - -"),
    ("b", "pass-reveal-traitor"),
    ("f", "pass-reveal-traitor"),
]

CMDS2 = [
    ("b", "predict harkonnen 5"),
    ("b", "place-token 1"),
    ("a", "place-token 4"),
    ("e", "place-token 7"),
    ("f", "place-token 10"),
    ("g", "place-token 13"),
    ("h", "place-token 16"),
    ("b", "select-traitor Piter-DeVries"),
    ("a", "select-traitor Stilgar"),
    ("f", "select-traitor Gurney-Halleck"),
    ("g", "select-traitor Jamis"),
    ("e", "select-traitor Chani"),
    ("f", "fremen-placement tabr:1,1,2 west:16:1,1,1 south:3:1,1,1,1"),
    ("b", "bene-gesserit-placement Polar-Sink -1"),
    ("f", "bid 1"),
    ("b", "choam-charity"),
    ("g", "bid 2"),
    ("h", "bid 3"),
    ("b", "pass"),
    ("a", "bid 4"),
    ("e", "pass"),
    ("f", "pass"),
    ("g", "pass"),
    ("h", "bid 5"),
    ("a", "pass"),
    ("a", "karama-pass-stop-extra"),
    ("b", "karama-pass-stop-extra"),
    ("e", "karama-pass-stop-extra"),
    ("f", "karama-pass-stop-extra"),
    ("g", "karama-pass-stop-extra"),
    ("g", "bid 1"),
    ("h", "pass"),
    ("b", "pass"),
    ("a", "pass"),
    ("e", "pass"),
    ("f", "pass"),
    ("h", "pass"),
    ("b", "pass"),
    ("a", "pass"),
    ("e", "pass"),
    ("f", "pass"),
    ("g", "bid 100"),
    ("g", "karama-free-bid"),
]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    random.seed(0)
    run_game(CMDS)
    random.seed(0)
    # run_game(CMDS2)
