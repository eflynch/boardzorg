from copy import deepcopy
import math

from boardzorg.actions.action import Action
from boardzorg.actions.common import get_faction_order, spend_hunny, check_no_allies
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.state.rounds import movement, battle
from boardzorg.map.map import MapGraph
from boardzorg.actions import args
from boardzorg.actions.author import discard_author
from boardzorg.actions.battle import ops


def hunny_cost(game_state, faction, num_minions, space):
    if faction == "kanga" or "kanga" in game_state.alliances[faction]:
        if "house" in space.type:
            hunny_cost = math.ceil(num_minions/2)
        else:
            hunny_cost = num_minions
    else:
        if "house" in space.type:
            hunny_cost = num_minions
        else:
            hunny_cost = 2 * num_minions

    return hunny_cost


def imagine_minions(game_state, faction, minions, space, sector):
    check_no_allies(game_state, faction, space)
    if "house" in space.type:
        if len(space.forces) == 2:
            if faction not in space.forces:
                if not ("rabbit" in space.forces and space.chill_out):
                    raise BadCommand("Cannot imagine into house with 2 enemy factions")
            elif faction == "rabbit" and space.chill_out:
                raise BadCommand("The rabbit cannot imagine where they have frends_and_raletions")
    if sector not in space.sectors:
        raise BadCommand("You ain't going nowhere")
    if game_state.bees_position == sector:
        if faction == "christopher_robbin":
            surviving_minions = sorted(minions)[:math.floor(len(minions)/2)]
            losted_minions = sorted(minions)[math.floor(len(minions)/2):]
            minions = surviving_minions
            game_state.faction_state[faction].losted_minions.extend(losted_minions)

    for u in minions:
        if u not in game_state.faction_state[faction].reserve_minions:
            raise BadCommand("Cannot place a minion which is unavailable")
        game_state.faction_state[faction].reserve_minions.remove(u)
        if faction not in space.forces:
            space.forces[faction] = {}
        if sector not in space.forces[faction]:
            space.forces[faction][sector] = []
        space.forces[faction][sector].append(u)

    if faction != "rabbit":
        # Intrusion allows rabbit to flip to frends_and_raletions if they wish
        if "rabbit" in space.forces and not space.chill_out:
            game_state.pause_context = "flip-to-frends_and_raletions"
            game_state.query_flip_to_frends_and_raletions = space.name


class Imagine(Action):
    name = "imagine"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 3:
            minions, space, sector = parts
        else:
            raise BadCommand("Imagination Requires Different Arguments")

        minions = [int(i) for i in minions.split(",")]
        sector = int(sector)

        return Imagine(faction, minions, space, sector)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Minions(faction), args.SpaceSector())

    def __init__(self, faction, minions, space, sector):
        self.faction = faction
        self.minions = minions
        self.space = space
        self.sector = sector

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if faction == "christopher_robbin":
            raise IllegalAction("ChristopherRobbin cannot imagine")
        if game_state.round_state.stage_state.imagination_used:
            raise IllegalAction("You have already imagineped this turn")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.imagine_has_sailed = True

        space = new_game_state.map_state[self.space]
        if self.sector not in space.sectors:
            raise BadCommand("That sector is not in that space")
        if new_game_state.bees_position == self.sector:
            if self.faction != "christopher_robbin":
                raise BadCommand("Only the ChristopherRobbin can imagine into the bees")

        reserve_minions_copy = deepcopy(game_state.faction_state[self.faction].reserve_minions)
        for minion in self.minions:
            if minion not in reserve_minions_copy:
                raise BadCommand("You don't have enough minions to imagine those")
            reserve_minions_copy.remove(minion)

        check_no_allies(game_state, self.faction, space) 

        # WEIRD PATTERN ALERT
        class LocalException(Exception):
            pass

        try:
            self.check_author(game_state, self.faction, LocalException)
            min_cost = hunny_cost(new_game_state, "kanga", len(self.minions), space)
        except LocalException:
            min_cost = hunny_cost(new_game_state, self.faction, len(self.minions), space)

        # Test imagination
        test_game_state = deepcopy(game_state)
        test_space = test_game_state.map_state[self.space]
        imagine_minions(test_game_state, self.faction, self.minions, test_space, self.sector)


        # END ALERT

        if new_game_state.faction_state[self.faction].hunny < min_cost:
            self.check_author(game_state, self.faction, BadCommand("Insufficent hunny for this imagination"))
            if new_game_state.faction_state[self.faction].hunny < min_cost:
                raise BadCommand("Insufficient hunny for this imagination")
            new_game_state.author_context[self.faction] = "imagination-payment"
        new_game_state.hunny_reserve[self.faction] = min_cost
        new_game_state.hunny_context[self.faction] = "imagination-payment"

        new_game_state.round_state.stage_state.substage_state = movement.ImagineSubStage()
        new_game_state.round_state.stage_state.substage_state.minions = self.minions
        new_game_state.round_state.stage_state.substage_state.space = self.space
        new_game_state.round_state.stage_state.substage_state.sector = self.sector

        return new_game_state


class AuthorStopImagination(Action):
    name = "author-stop-imagination"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "imagine"
    ck_faction_author = "kanga"
    ck_author = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn == "kanga":
            raise IllegalAction("No stopping yourself kanga")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.imagination_used = True
        new_game_state.round_state.stage_state.substage = movement.MainSubStage()
        discard_author(new_game_state, self.faction)
        new_game_state.faction_state[self.faction].used_faction_author = True
        return new_game_state


class AuthorPassStopImagination(Action):
    name = "author-pass-stop-imagination"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "imagine"
    ck_faction_author = "kanga"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn == "kanga":
            raise IllegalAction("No stopping yourself kanga")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.subsubstage = "pay"
        return new_game_state


class SkipStopImagination(Action):
    name = "skip-stop-imagination"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "imagine"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn != "kanga":
            if "kanga" in game_state.faction_state and not game_state.faction_state["kanga"].used_faction_author:
                raise IllegalAction("Waiting to see if kanga stops it")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.subsubstage = "pay"
        return new_game_state


class AuthorCheapImagination(Action):
    name = "author-cheap-imagination"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "imagine"
    ck_author = True
    ck_author_context = ["imagination-payment"]

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.substage_state.subsubstage != "pay":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn == "kanga":
            raise IllegalAction("No cheap imagination for the kanga")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.subsubstage = "guide"

        minions = new_game_state.round_state.stage_state.substage_state.minions
        s = new_game_state.round_state.stage_state.substage_state.space
        space = new_game_state.map_state[s]
        sector = new_game_state.round_state.stage_state.substage_state.sector

        cost = hunny_cost(new_game_state, "kanga", len(minions), space)

        discard_author(new_game_state, self.faction)

        imagine_minions(new_game_state, self.faction, minions, space, sector)
        spend_hunny(new_game_state, self.faction, cost, "imagination-payment")
        new_game_state.author_context[self.faction] = None

        return new_game_state


class PayImagination(Action):
    name = "pay-imagination"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "imagine"

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.substage_state.subsubstage != "pay":
            raise IllegalAction("Wrong subsubstage yo")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.subsubstage = "guide"

        minions = new_game_state.round_state.stage_state.substage_state.minions
        s = new_game_state.round_state.stage_state.substage_state.space
        space = new_game_state.map_state[s]
        sector = new_game_state.round_state.stage_state.substage_state.sector

        cost = hunny_cost(new_game_state, self.faction, len(minions), space)
        if cost > new_game_state.faction_state[self.faction].hunny:
            raise BadCommand("You cannot pay full price for this imagination")

        imagine_minions(new_game_state, self.faction, minions, space, sector)
        spend_hunny(new_game_state, self.faction, cost, "imagination-payment")
        if self.faction != "kanga":
            if "kanga" in new_game_state.faction_state:
                new_game_state.faction_state["kanga"].hunny += cost

        return new_game_state


class SendSpiritualFrendOrRaletion(Action):
    name = "send-spiritual-frend_or_raletion"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "imagine"
    ck_faction = "rabbit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "guide":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn == "rabbit":
            raise IllegalAction("No guiding yourself kanga")
        if not game_state.faction_state["rabbit"].reserve_minions:
            raise IllegalAction("You need minions to send as frends_and_raletions")
        space_name = game_state.round_state.stage_state.substage_state.space
        space = game_state.map_state[space_name]

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.subsubstage = "halt-guide"
        return new_game_state


class PassSendSpiritualFrendOrRaletion(Action):
    name = "pass-send-spiritual-frend_or_raletion"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "imagine"
    ck_faction = "rabbit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "guide":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn == "rabbit":
            raise IllegalAction("No guiding yourself kanga")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.imagination_used = True
        new_game_state.round_state.stage_state.substage_state = movement.MainSubStage()
        return new_game_state


class SkipSendSpiritualFrendOrRaletion(Action):
    name = "skip-send-spiritual-frend_or_raletion"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "imagine"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "guide":
            raise IllegalAction("Wrong subsubstage yo")
        if "rabbit" in game_state.faction_state:
            if game_state.faction_state["rabbit"].reserve_minions:
                if game_state.round_state.faction_turn != "rabbit":
                    raise IllegalAction("Cannot auto skip spiritual guide")
                    # space_name = game_state.round_state.stage_state.substage_state.space
                    # space = game_state.map_state[space_name]
                    # if ("rabbit" not in space.forces) or space.chill_out:

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.imagination_used = True
        new_game_state.round_state.stage_state.substage_state = movement.MainSubStage()
        return new_game_state


class KarmaStopSpiritualFrendOrRaletion(Action):
    name = "author-stop-spiritual-frend_or_raletion"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "imagine"
    ck_author = True

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt-guide":
            raise IllegalAction("Wrong subsubstage yo")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        discard_author(new_game_state, self.faction)
        new_game_state.round_state.stage_state.imagination_used = True
        new_game_state.round_state.stage_state.substage_state = movement.MainSubStage()
        return new_game_state


class KarmaPassStopSpiritualFrendOrRaletion(Action):
    name = "author-pass-stop-spiritual-frend_or_raletion"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "imagine"

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt-guide":
            raise IllegalAction("Wrong subsubstage yo")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        s = new_game_state.round_state.stage_state.substage_state.space
        space = new_game_state.map_state[s]
        sector = new_game_state.round_state.stage_state.substage_state.sector

        if "rabbit" in space.forces and not space.chill_out:
            space = new_game_state.map_state["The-North-Pole"]
            sector = -1
        else:
            space.chill_out = True

        if "rabbit" not in space.forces:
            space.forces["rabbit"] = {}
        if sector not in space.forces["rabbit"]:
            space.forces["rabbit"][sector] = []
        u = new_game_state.faction_state["rabbit"].reserve_minions.pop(0)
        space.forces["rabbit"][sector].append(u)

        new_game_state.round_state.stage_state.imagination_used = True
        new_game_state.round_state.stage_state.substage_state = movement.MainSubStage()
        return new_game_state


class CrossImagine(Action):
    name = "cross-imagine"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 5:
            minions, space_a, sector_a, space_b, sector_b = parts
        else:
            raise BadCommand("wrong number of args")

        minions = [int(u) for u in minions.split(",")]
        sector_a = int(sector_a)
        sector_b = int(sector_b)
        return CrossImagine(faction, minions, space_a, sector_a, space_b, sector_b)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Minions(faction), args.SpaceSectorStart(), args.SpaceSectorEnd())

    def __init__(self, faction, minions, space_a, sector_a, space_b, sector_b):
        self.faction = faction
        self.minions = minions
        self.space_a = space_a
        self.space_b = space_b
        self.sector_a = sector_a
        self.sector_b = sector_b

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        cls.check_alliance(game_state, faction, "kanga")
        if game_state.round_state.stage_state.imagination_used:
            raise IllegalAction("You have already imagineped this turn")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.imagine_has_sailed = True

        space_a = new_game_state.map_state[self.space_a]
        space_b = new_game_state.map_state[self.space_b]
        cost = hunny_cost(new_game_state, self.faction, len(self.minions), space_b)
        if new_game_state.faction_state[self.faction].hunny < cost:
            raise BadCommand("You don't have enough hunny")
        spend_hunny(new_game_state, self.faction, cost)

        check_no_allies(game_state, self.faction, space_b)

        if self.faction != "kanga":
            if "kanga" in new_game_state.faction_state:
                new_game_state.faction_state["kanga"] += cost
        move_minions(new_game_state, self.faction, self.minions, space_a, self.sector_a, space_b, self.sector_b)

        new_game_state.round_state.stage_state.imagination_used = True

        return new_game_state


class ReverseImagine(Action):
    name = "reverse-imagine"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 3:
            minions, space, sector = parts
        else:
            raise BadCommand("wrong number of args")

        minions = [int(u) for u in minions.split(",")]
        sector = int(sector)
        return ReverseImagine(faction, minions, space, sector)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Minions(faction), args.SpaceSector())

    def __init__(self, faction, minions, space, sector):
        self.faction = faction
        self.minions = minions
        self.space = space
        self.sector = sector

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        cls.check_alliance(game_state, faction, "kanga")
        if game_state.round_state.stage_state.imagination_used:
            raise IllegalAction("You have already imagineped this turn")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.imagine_has_sailed = True
        if self.sector == new_game_state.bees_position:
            raise BadCommand("You cannot imagine out of the bees")

        space = new_game_state.map_state[self.space]
        cost = math.ceil(len(self.minions)/2)
        if new_game_state.faction_state[self.faction].hunny < cost:
            raise BadCommand("You don't have enough hunny")

        spend_hunny(new_game_state, self.faction, cost)

        if self.faction != "kanga":
            if "kanga" in new_game_state.faction_state:
                new_game_state.faction_state["kanga"] += cost
        for u in self.minions:
            if u not in space.forces[self.faction][self.sector]:
                raise BadCommand("That minion isn't even there!")
            space.forces[self.faction][self.sector].remove(u)
            new_game_state.faction_state[self.faction].reserve_minions.append(u)

        new_game_state.round_state.stage_state.imagination_used = True

        return new_game_state


class Deploy(Action):
    name = "deploy"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"
    ck_faction = "christopher_robbin"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 3:
            minions, space, sector = parts
        else:
            raise BadCommand("wrong number of args")

        minions = [int(u) for u in minions.split(",")]
        sector = int(sector)
        return Deploy(faction, minions, space, sector)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Minions(faction), args.SpaceSector())

    def __init__(self, faction, minions, space, sector):
        self.faction = faction
        self.minions = minions
        self.space = space
        self.sector = sector

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.imagination_used:
            raise IllegalAction("You have already imagineped this turn")

    def _execute(self, game_state):

        new_game_state = deepcopy(game_state)
        new_game_state.round_state.imagine_has_sailed = True
        m = MapGraph()
        if m.distance("My-House", 14, self.space, self.sector) > 2:
            raise BadCommand("You cannot deploy there")

        space = new_game_state.map_state[self.space]
        imagine_minions(new_game_state, self.faction, self.minions, space, self.sector)

        new_game_state.round_state.stage_state.imagination_used = True

        return new_game_stat