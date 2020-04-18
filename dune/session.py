import logging
import json

from dune.actions.action import Action
from dune.actions.args import Args
from dune.exceptions import BadCommand, IllegalAction
from dune.state.game import GameState

logger = logging.getLogger(__name__)

HOST_ACTIONS = ["undo"]


class HostAction:
    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return Args()


def handle_host_actions(session, cmd):
    if cmd == "undo":
        session.undo()


class Session:
    def __init__(self, init_state, seed=None):
        self.seed = seed
        self.game_log = [init_state]
        self.action_log = []
        self.command_log = []
        self.su_commands = {}
        self._next_command_index = 0
        self.execute_supervisor()

    def execute_supervisor(self):
        supervisor_actions = Action.get_valid_actions(self.game_log[-1], None)
        if len(supervisor_actions) > 1:
            logger.critical("SUPERVISOR ERROR: {}".format(supervisor_actions))
        for s in supervisor_actions:
            self.execute_action(supervisor_actions[s]())
            if self._next_command_index not in self.su_commands:
                self.su_commands[self._next_command_index] = []
            self.su_commands[self._next_command_index].append(supervisor_actions[s].name)

    def execute_action(self, action):
        old_state = self.game_log[-1]
        new_state = action.execute(game_state=old_state)
        logger.debug("Executing: {}".format(action))
        self.game_log.append(new_state)
        self.action_log.append(action)
        self.execute_supervisor()

    def undo(self):
        self.game_log.pop()
        self.action_log.pop()
        self.command_log.pop()

    def handle_cmd(self, role, cmd):
        if role in ('host',):
            if cmd in HOST_ACTIONS:
                handle_host_actions(self, cmd)
                return
            else:
                raise BadCommand("{} not a host action".format(cmd))

        faction = role
        valid_actions = Action.get_valid_actions(self.game_log[-1], faction)
        action_type = cmd.split(" ")[0]
        args = " ".join(cmd.split(" ")[1:])
        if action_type not in valid_actions:
            action = Action.get_action(action_type)
            if action:
                action.check(self.game_log[-1], faction)
            else:
                raise BadCommand("Not a known action", action_type)
        action = valid_actions[action_type].parse_args(faction, args)
        self._next_command_index += 1
        self.execute_action(action)
        self.command_log.append((faction, cmd))

    def get_visible_state(self, role):
        return self.game_log[-1].visible(role)

    def get_valid_actions(self, role):
        if role in ('host',):
            return {a: HostAction() for a in HOST_ACTIONS}
        faction = role
        return Action.get_valid_actions(self.game_log[-1], faction)

    def get_factions_in_play(self):
        return list(self.game_log[0].faction_state.keys())

    def get_visible_command_log(self, faction):
        def _redact(command):
            (cmd_faction, cmd) = command
            redacted = ["predict", "select-traitor", "commit-plan"]
            if cmd.split(" ")[0] in redacted:
                if cmd_faction != faction:
                    return (cmd_faction, cmd.split(" ")[0] + " ?¿?¿?")
            return command
        redacted_commands = list(map(_redact, self.command_log))
        for cmd_idx in reversed(sorted(self.su_commands)):
            for su_cmd in self.su_commands[cmd_idx]:
                redacted_commands.insert(cmd_idx, ("su", su_cmd))
        return redacted_commands

    @staticmethod
    def new_session(factions=None, treachery_deck=None, seed=None):
        init_state = GameState.new_shuffle(factions, treachery_deck, seed)
        return Session(init_state=init_state, seed=seed)

    @staticmethod
    def serialize(session):
        init_state = session.game_log[0]
        to_json = {
            "seed": session.seed,
            "factions": init_state.factions,
            "treachery_deck": init_state.treachery_deck,
            "spice_deck": init_state.spice_deck,
            "traitor_deck": init_state.traitor_deck,
            "storm_deck": init_state.storm_deck,
            "random_choice_deck": init_state.random_choice_deck,
            "command_log": session.command_log
        }
        return json.dumps(to_json)

    @staticmethod
    def realize(serialized_session):
        if type(serialized_session) is dict:
            from_json = serialized_session
        else:
            from_json = json.loads(serialized_session)
        init_state = GameState(
            factions=from_json["factions"],
            treachery_deck=from_json["treachery_deck"],
            spice_deck=from_json["spice_deck"],
            traitor_deck=list(map(tuple, from_json["traitor_deck"])),
            storm_deck=from_json["storm_deck"],
            random_choice_deck=from_json.get("random_choice_deck", None)
        )
        session = Session(init_state, from_json["seed"])

        for f, cmd in from_json["command_log"]:
            try:
                session.handle_cmd(f, cmd)
            except BadCommand as e:
                print("ERROR:", cmd, e)
            except IllegalAction as e:
                print("ERROR", cmd, e)
        return session
