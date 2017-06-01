
from dune.session import SessionState
from dune.exceptions import IllegalAction

import random


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
    session = SessionState(debug=True)

    for faction, cmd in cmds:
        try:
            session.handle_cmd(translate_faction(faction), cmd)
        except IllegalAction as e:
            print("    IllegalAction: ", e)

    final_state = session.game_log[-1]


CMDS = [
    ("b", "predict harkonnen 5"),
    ("b", "place-token 1"),
    ("a", "place-token 4"),
    ("e", "place-token 7"),
    ("f", "place-token 10"),
    ("g", "place-token 13"),
    ("h", "place-token 16"),
    ("b", "select-traitor Thufir-Hawat"),
    ("a", "select-traitor Representative"),
    ("f", "select-traitor Lady-Jessica"),
    ("g", "select-traitor Margot-Lady-Fenring"),
    ("e", "select-traitor Chani"),
    ("f", "fremen-placement tabr:1,1,2 west:16:1,1,1 south:3:1,1,1,1"),
    ("b", "bene-gesserit-placement Polar-Sink -1"),
    ("g", "bid 1"),
    ("b", "choam-charity"),
    ("h", "bid 2"),
    ("b", "bid 3"),
    ("a", "pass"),
    ("e", "bid 4"),
    ("f", "pass"),
    ("g", "bid 5"),
    ("h", "pass"),
    ("b", "pass"),
    ("e", "pass"),
    ("g", "karama-pass-free-bid"),
    ("h", "pass"),
    ("b", "pass"),
    ("a", "pass"),
    ("e", "pass"),
    ("f", "pass"),
    ("g", "pass"),
]


if __name__ == "__main__":
    random.seed(0)
    run_game(CMDS)
