from copy import deepcopy

from boardzorg.actions import args
from boardzorg.actions.action import Action
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.actions.retrieval import parse_retrieval_minions, parse_retrieval_character
from boardzorg.actions.retrieval import revive_minions, revive_character
from boardzorg.map.map import MapGraph
from boardzorg.actions.battle import ops
from boardzorg.actions.movement import parse_movement_args, perform_movement


def discard_provisions(game_state, faction, provisions):
    game_state.faction_state[faction].provisions.remove(provisions)
    game_state.provisions_discard.insert(0, provisions)


class HoneyJar(Action):
    name = "honey-jar"
    ck_provisions = "Honey-Jar"
    non_blocking = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.pause.append(self.faction)
        discard_provisions(new_game_state, self.faction, "Honey-Jar")
        return new_game_state


class Bath(Action):
    name = "bath"
    ck_provisions = "Bath"
    non_blocking = True

    @classmethod
    def parse_args(cls, faction, args):
        if not args:
            return Bath(faction, [], None)
        if "1" in args or "2" in args:
            minions = args
            character = ""
        else:
            character = args
            minions = ""
        return Bath(faction, parse_retrieval_minions(minions), parse_retrieval_character(character))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Union(
            args.RetrievalMinions(game_state.faction_state[faction].lost_minions, max_minions=5, single_2=False),
            args.RetrievalCharacter(game_state.faction_state[faction].lost_characters)
        )

    def __init__(self, faction, minions, character):
        self.faction = faction
        self.minions = minions
        self.character = character

    @classmethod
    def _check(cls, game_state, faction):
        if (not game_state.faction_state[faction].lost_minions) and \
           game_state.faction_state[faction].lost_characters:
            raise IllegalAction("You don't have anything to revive")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        if self.character and self.minions:
            raise BadCommand("You must pick minions or a character")

        if self.character:
            if self.character not in new_game_state.faction_state[self.faction].lost_characters:
                raise BadCommand("That character is not revivable")
            revive_character(self.character, self.faction, new_game_state)

        if self.minions:
            if len(self.minions) > 5:
                raise BadCommand("You can only revive up to five minions")
            revive_minions(self.minions, self.faction, new_game_state)

        discard_provisions(new_game_state, self.faction, "Bath")
        return new_game_state


class Balloon(Action):
    name = "balloon"
    ck_provisions = "Balloon"
    ck_round = "control"
    non_blocking = True

    @classmethod
    def _check(cls, game_state, faction):
        someone_close = False
        m = MapGraph()
        for space in game_state.map_state.values():
            if faction in space.forces:
                for sector in space.forces[faction]:
                    if m.distance(space.name, sector, "Bee-Tree", 7) <= 1:
                        someone_close = True
                        break
                    if m.distance(space.name, sector, "Bee-Tree", 8) <= 1:
                        someone_close = True
                        break

        if not someone_close:
            raise IllegalAction("You cannot get to the umbrella wall")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.umbrella_wall = False

        ops.lost_all_minions(new_game_state, "Bee-Tree")

        discard_provisions(new_game_state, self.faction, "Balloon")
        return new_game_state


class Expedition(Action):
    name = "expedition"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"
    ck_provisions = "Expedition"
    non_blocking = True

    @classmethod
    def parse_args(cls, faction, args):
        return Expedition(faction, parse_movement_args(args))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Minions(faction), args.SpaceSectorStart(), args.SpaceSectorEnd())

    def __init__(self, faction, move_args):
        self.faction = faction
        self.move_args = move_args

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        perform_movement(new_game_state,
                         self.faction,
                         *self.move_args)
        discard_provisions(new_game_state, self.faction, "Expedition")
        return new_game_state
