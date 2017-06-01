from dune.actions.action import Action
from dune.actions import nexus
from dune.exceptions import IllegalAction

# These unsed imports register the Action classes
from dune.actions import setup, storm, spice, nexus, bidding  # noqa # pylint: disable=unused-import
from dune.actions import revival, movement, battle, collection  # noqa # pylint: disable=unused-import


def get_supervisor_actions(game_state):
    valid_actions = get_valid_actions(game_state, None)
    if valid_actions:
        if len(valid_actions) > 1:
            print(valid_actions)
            raise Exception("We got a problem with supervisor actions")
        return valid_actions
    return {}

    round_state = game_state.round_state
    if round_state.round == "nexus":
        if not round_state.proposals_done and nexus.alliances_work(game_state):
            return nexus.ResolveAlliance()
        if not nexus.fremen_allies_present(game_state):
            return nexus.EndNexus()
        if round_state.worm_done:
            return nexus.EndNexus()


def get_valid_actions(game_state, faction):
    valid_actions = {}
    for action in Action.registry:
        try:
            Action.registry[action].check(game_state, faction)
        except IllegalAction:
            pass
        else:
            valid_actions[action] = Action.registry[action]

    for action in Action.round_registry[game_state.round_state.round]:
        try:
            Action.round_registry[game_state.round_state.round][action].check(game_state, faction)
        except IllegalAction:
            pass
        else:
            valid_actions[action] = Action.round_registry[game_state.round_state.round][action]
    return valid_actions
