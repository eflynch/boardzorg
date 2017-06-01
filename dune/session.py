import threading
from queue import Queue

from dune.actions.manager import get_valid_actions, get_supervisor_actions
from dune.exceptions import IllegalAction, BadCommand
from dune.state.state import GameState


class SessionState:
    def __init__(self, debug=False):
        self.game_log = [GameState()]
        self.action_log = []
        self.debug = debug

    def execute_action(self, action):
        old_state = self.game_log[-1]
        new_state = action.execute(game_state=old_state)
        new_state.assert_valid()
        self.game_log.append(new_state)
        self.action_log.append(action)
        supervisor_actions = get_supervisor_actions(self.game_log[-1])
        for s in supervisor_actions:
            print("Supervisor:: {}".format(s))
            self.execute_action(supervisor_actions[s]())

    def handle_cmd(self, faction, cmd):
        valid_actions = get_valid_actions(self.game_log[-1], faction)
        if self.debug:
            print("Choices: " + " ".join(list(valid_actions.keys())))
        action_type = cmd.split(" ")[0]
        args = " ".join(cmd.split(" ")[1:])
        if self.debug:
            print("    {}:: {} : {}".format(faction, action_type, args))
        if action_type not in valid_actions:
            raise IllegalAction("That Action is not possible at this time")

        action = valid_actions[action_type].parse_args(faction, args)
        self.execute_action(action)


def server(session, q):
    while True:
        faction, cmd = q.get()
        try:
            session.handle_cmd(faction, cmd)
        except IllegalAction as e:
            print(e)
        except BadCommand as e:
            print(e)


def client(q):
    faction = "atreides"
    while True:
        cmd = input("~~> ")
        if not len(cmd):
            continue
        cmd = cmd.lower()
        q.put((faction, cmd))


if __name__ == "__main__":
    session = SessionState(debug=True)
    q = Queue()

    t1 = threading.Thread(target=client, args=(q,))
    t2 = threading.Thread(target=server, args=(session, q))
    t2.start()
    t1.start()
