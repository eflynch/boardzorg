from state import GameState
from actions import get_valid_actions, get_supervisor_action
from factions import FACTIONS

from exceptions import IllegalAction, BadCommand

import pickle


class SessionState:
    def __init__(self):
        self.game_log = [GameState()]
        self.action_log = []

    def execute_action(self, action):
        old_state = self.game_log[-1]
        new_state = action.execute(game_state=old_state)
        new_state.assert_valid()
        self.game_log.append(new_state)
        self.action_log.append(action)
        supervisor_action = get_supervisor_action(self.game_log[-1])
        if supervisor_action:
            self.execute_action(supervisor_action)

    def handle_cmd(self, faction, cmd):
        valid_actions = get_valid_actions(self.game_log[-1], faction)
        action_type = cmd.split(" ")[0]
        args = " ".join(cmd.split(" ")[1:])
        if action_type not in valid_actions:
            raise IllegalAction("That Action is not possible at this time")

        action = valid_actions[action_type].parse_args(faction, args)
        self.execute_action(action)


if __name__ == "__main__":
    session = SessionState()

    faction = "atreides"

    while True:
        cmd = input("~~> ")
        if not len(cmd):
            continue
        cmd = cmd.lower()

        if len(cmd) and cmd[0] == ":":
            if cmd == ":exit":
                break
            if ":open" in cmd:
                session_name = cmd.split(" ")[1]
                with open(session_name) as f:
                    session = pickle.load(f)

            if ":save" in cmd:
                session_name = cmd.split(" ")[1]
                with open(session_name, "wb") as f:
                    pickle.dump(session, f)

            if ":faction" in cmd:
                new_faction = cmd.split(" ")[1]
                if new_faction not in FACTIONS:
                    print("Not a valid faction")
                else:
                    faction = new_faction
        else:
            try:
                session.handle_cmd(faction, cmd)
            except IllegalAction as e:
                print(e)
            except BadCommand as e:
                print(e)
