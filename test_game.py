
from dune.session import Session
from dune.exceptions import IllegalAction, BadCommand

import random
import json
import logging


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
        try:
            session.handle_cmd(translate_faction(faction), cmd)
        except IllegalAction as e:
            print("    IllegalAction: ", e)
        except BadCommand as e:
            print("    BadComand: ", e)

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
    ("h", "bid 1"),
    ("b", "pass"),
    ("a", "pass"),
    ("e", "pass"),
    ("f", "pass"),
    ("g", "pass"),
    ("g", "karama-stop-extra"),
    ("b", "pass"),
    ("a", "pass"),
    ("e", "pass"),
    ("f", "pass"),
    ("g", "pass"),
    ("h", "pass"),
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
    run_game(CMDS2)
