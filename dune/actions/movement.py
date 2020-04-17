from copy import deepcopy
import math

from dune.actions.action import Action
from dune.actions.common import get_faction_order
from dune.exceptions import IllegalAction, BadCommand
from dune.state.rounds import movement, battle
from dune.map.map import MapGraph
from dune.actions import args
from dune.actions.karama import discard_karama
from dune.actions.spice import spend_spice


def ship_units(game_state, faction, units, space, sector):
    if "stronghold" in space.type:
        if len(space.forces) > 1:
            if faction not in space.forces:
                if not ("bene-gesserit" in space.forces and space.coexist):
                    raise BadCommand("Cannot ship into stronghold with 2 enemy factions")
            elif faction == "bene-gesserit" and space.coexist:
                raise BadCommand("The bene-gesserit cannot ship in here because of occupation constraints")
    if sector not in space.sectors:
        raise BadCommand("You ain't going nowhere")

    if game_state.storm_position == sector:
        if faction == "fremen":
            surviving_units = sorted(units)[:math.floor(len(units)/2)]
            tanked_units = sorted(units)[math.floor(len(units)/2):]
            units = surviving_units
            game_state.faction_state[faction].tanked_units.extend(tanked_units)

    for u in units:
        if u not in game_state.faction_state[faction].reserve_units:
            raise BadCommand("Cannot place a unit which is unavailable")
        game_state.faction_state[faction].reserve_units.remove(u)
        if faction not in space.forces:
            space.forces[faction] = {}
        if sector not in space.forces[faction]:
            space.forces[faction][sector] = []
        space.forces[faction][sector].append(u)

    if faction != "bene-gesserit":
        # Intrusion allows bene-gesserit to flip to advisors if they wish
        if "bene-gesserit" in space.forces and not space.coexist:
            game_state.round_state.stage_state.query_flip_to_advisors = space.name


def move_units(game_state, faction, units, space_a, sector_a, space_b, sector_b):
    if "stronghold" in space_b.type:
        total_forces = len(space_b.forces)
        if "bene-gesserit" in space_b.forces and space_b.coexist:
            total_forces -= 1
        if total_forces > 1:
            if faction not in space_b.forces:
                raise BadCommand("Cannot move into stronghold with 2 enemy factions")
    if sector_b not in space_b.sectors:
        raise BadCommand("You ain't going nowhere")

    if sector_a not in space_a.sectors:
        raise BadCommand("You ain't coming from nowhere")

    if game_state.storm_position == sector_b:
        if faction == "fremen":
            surviving_units = sorted(units)[:math.floor(len(units)/2)]
            tanked_units = sorted(units)[math.floor(len(units)/2):]
            units = surviving_units
            game_state.faction_state[faction].tanked_units.extend(tanked_units)
        else:
            raise BadCommand("You cannot move into the storm")
    if game_state.storm_position == sector_a:
        if faction != "fremen":
            raise BadCommand("You cannot move from the storm")

    if faction not in space_b.forces:
        space_b.forces[faction] = {}
    if sector_b not in space_b.forces[faction]:
        space_b.forces[faction][sector_b] = []

    if faction not in space_a.forces:
        raise BadCommand("You don't have anything there")
    if sector_a not in space_a.forces[faction]:
        raise BadCommand("You don't have anything there")

    for u in units:
        if u not in space_a.forces[faction][sector_a]:
            raise BadCommand("You ain't got the troops")
        space_a.forces[faction][sector_a].remove(u)
        space_b.forces[faction][sector_b].append(u)

    if all(space_a.forces[faction][s] == [] for s in space_a.forces[faction]):
        del space_a.forces[faction]

    # Update Coexist flags

    if faction == "bene-gesserit":

        # Advisors flip to Fighters if fighters join them
        # Also If bene-gesserit not present or alone, there can be no advisors
        if not space_a.coexist or len(space_b.forces) == 1:
            space_b.coexist = False

        # Advisors may flip to fighters if they move somewhere occupied
        else:
            game_state.round_state.stage_state.query_flip_to_fighters = space_b.name

    else:
        # Intrusion allows bene-gesserit to flip to advisors if they wish
        if "bene-gesserit" in space_b.forces and not space_b.coexist:
            game_state.round_state.stage_state.query_flip_to_advisors = space_b.name

    # If bene-gesserit not present or alone, there can be no advisors
    if "bene-gesserit" not in space_a.forces or len(space_a.forces) == 1:
        space_a.coexist = False


def spice_cost(game_state, faction, num_units, space):
    if faction == "guild" or "guild" in game_state.alliances[faction]:
        if "stronghold" in space.type:
            spice_cost = math.ceil(num_units/2)
        else:
            spice_cost = num_units
    else:
        if "stronghold" in space.type:
            spice_cost = num_units
        else:
            spice_cost = 2 * num_units

    return spice_cost


class KaramaBlockGuildTurnChoice(Action):
    name = "karama-block-guild-turn-choice"
    ck_round = "movement"
    ck_stage = "setup"
    ck_karama = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "guild":
            raise IllegalAction("The guild cannot do that")
        if faction in game_state.round_state.stage_state.karama_passes:
            raise IllegalAction("You have already passed this option")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.guild_choice_blocked = True
        faction_order = get_faction_order(game_state)
        new_game_state.round_state.faction_turn = faction_order[0]
        new_game_state.round_state.turn_order = faction_order
        new_game_state.round_state.stage_state = movement.TurnStage()
        discard_karama(new_game_state, self.faction)
        return new_game_state


class KaramaPassBlockGuildTurnChoice(Action):
    name = "karama-pass-block-guild-turn-choice"
    ck_round = "movement"
    ck_stage = "setup"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "guild":
            raise IllegalAction("The guild cannot do that")
        if faction in game_state.round_state.stage_state.karama_passes:
            raise IllegalAction("You have already passed this option")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_passes.append(self.faction)
        return new_game_state


class SkipKaramaGuildTurnChoice(Action):
    name = "skip-karama-block-guild-turn-choice"
    ck_round = "movement"
    ck_stage = "setup"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "guild" in game_state.faction_state:
            if len(game_state.round_state.stage_state.karama_passes) != len(game_state.faction_state) - 1:
                raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        faction_order = get_faction_order(game_state)
        if "guild" in faction_order:
            faction_order.remove("guild")
            faction_order.insert(0, "guild")
        new_game_state.round_state.turn_order = faction_order
        new_game_state.round_state.faction_turn = faction_order[0]
        new_game_state.round_state.stage_state = movement.TurnStage()
        return new_game_state


class GuildPass(Action):
    name = "guild-pass-turn"
    ck_round = "movement"
    ck_stage = "turn"
    ck_faction = "guild"
    ck_substage = "main"

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.guild_choice_blocked:
            raise IllegalAction("The guild choice has been blocked by karama")
        if game_state.round_state.stage_state.shipment_used:
            raise IllegalAction("You have already started your turn")
        if game_state.round_state.stage_state.movement_used:
            raise IllegalAction("You have already started your turn")
        if game_state.round_state.turn_order[-1] == "guild":
            raise IllegalAction("You last fool")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        idx = new_game_state.round_state.turn_order.index("guild")
        new_game_state.round_state.turn_order.remove("guild")
        new_game_state.round_state.turn_order.insert(idx+1, "guild")
        new_game_state.round_state.faction_turn = new_game_state.round_state.turn_order[idx]
        return new_game_state


class EndMovementTurn(Action):
    name = "end-movement"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)

        if game_state.round_state.stage_state.query_flip_to_advisors:
            raise IllegalAction("Query advisor flip in progress")

        if game_state.round_state.stage_state.query_flip_to_fighters:
            raise IllegalAction("Query fighter flip in progress")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        idx = new_game_state.round_state.turn_order.index(self.faction)
        if idx == len(new_game_state.round_state.turn_order) - 1:
            new_game_state.round_state = battle.BattleRound()
            return new_game_state
        new_game_state.round_state.faction_turn = new_game_state.round_state.turn_order[idx + 1]
        new_game_state.round_state.stage_state = movement.TurnStage()
        return new_game_state


class AutoEndMovementTurn(Action):
    name = "auto-end-movement"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.round_state.stage_state.shipment_used:
            raise IllegalAction("Shipment still possible")

        if not game_state.round_state.stage_state.movement_used:
            raise IllegalAction("Movement still possible")

        if game_state.round_state.stage_state.query_flip_to_advisors:
            raise IllegalAction("Query advisor flip in progress")

        if game_state.round_state.stage_state.query_flip_to_fighters:
            raise IllegalAction("Query fighter flip in progress")

        faction_turn = game_state.round_state.faction_turn
        if "Hajr" in game_state.faction_state[faction_turn].treachery:
            raise IllegalAction("Still could use Hajr card")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        faction_turn = new_game_state.round_state.faction_turn
        idx = new_game_state.round_state.turn_order.index(faction_turn)
        if idx == len(new_game_state.round_state.turn_order) - 1:
            new_game_state.round_state = battle.BattleRound()
            return new_game_state
        new_game_state.round_state.faction_turn = new_game_state.round_state.turn_order[idx + 1]
        new_game_state.round_state.stage_state = movement.TurnStage()
        return new_game_state


class Ship(Action):
    name = "ship"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 3:
            units, space, sector = parts
        else:
            raise BadCommand("Shipment Requires Different Arguments")

        units = [int(i) for i in units.split(",")]
        sector = int(sector)

        return Ship(faction, units, space, sector)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Units(faction), args.SpaceSector())

    def __init__(self, faction, units, space, sector):
        self.faction = faction
        self.units = units
        self.space = space
        self.sector = sector

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if faction == "fremen":
            raise IllegalAction("Fremen cannot ship")
        if game_state.round_state.stage_state.shipment_used:
            raise IllegalAction("You have already shipped this turn")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.ship_has_sailed = True

        space = new_game_state.map_state[self.space]
        if self.sector not in space.sectors:
            raise BadCommand("That sector is not in that space")
        if new_game_state.storm_position == self.sector:
            if self.faction != "fremen":
                raise BadCommand("Only the Fremen can ship into the storm")

        # WEIRD PATTERN ALERT
        class LocalException(Exception):
            pass

        try:
            self.check_karama(game_state, self.faction, LocalException)
            min_cost = spice_cost(new_game_state, "guild", len(self.units), space)
        except LocalException:
            min_cost = spice_cost(new_game_state, self.faction, len(self.units), space)

        # END ALERT

        if new_game_state.faction_state[self.faction].spice < min_cost:
            self.check_karama(game_state, self.faction, BadCommand("Insufficent spice for this shipment"))
            if new_game_state.faction_state[self.faction].spice < min_cost:
                raise BadCommand("Insufficient spice for this shipment")
            new_game_state.karama_context[self.faction] = "shipment-payment"
        new_game_state.spice_reserve[self.faction] = min_cost
        new_game_state.spice_context[self.faction] = "shipment-payment"

        new_game_state.round_state.stage_state.substage_state = movement.ShipSubStage()
        new_game_state.round_state.stage_state.substage_state.units = self.units
        new_game_state.round_state.stage_state.substage_state.space = self.space
        new_game_state.round_state.stage_state.substage_state.sector = self.sector

        return new_game_state


class KaramaStopShipment(Action):
    name = "karama-stop-shipment"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"
    ck_faction = "guild"
    ck_karama = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn == "guild":
            raise IllegalAction("No stopping yourself guild")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.shipment_used = True
        new_game_state.round_state.stage_state.substage = movement.MainSubStage()
        discard_karama(game_state, self.faction)
        return new_game_state


class KaramaPassStopShipment(Action):
    name = "karama-pass-stop-shipment"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"
    ck_faction = "guild"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn == "guild":
            raise IllegalAction("No stopping yourself guild")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.subsubstage = "pay"
        return new_game_state


class SkipStopShipment(Action):
    name = "skip-stop-shipment"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn != "guild":
            if "guild" in game_state.faction_state:
                raise IllegalAction("Waiting to see if guild stops it")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.subsubstage = "pay"
        return new_game_state


class KaramaCheapShipment(Action):
    name = "karama-cheap-shipment"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"
    ck_karama = True
    ck_karama_context = ["shipment-payment"]

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.substage_state.subsubstage != "pay":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn == "guild":
            raise IllegalAction("No cheap shipment for the guild")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.subsubstage = "guide"

        units = new_game_state.round_state.stage_state.substage_state.units
        s = new_game_state.round_state.stage_state.substage_state.space
        space = new_game_state.map_state[s]
        sector = new_game_state.round_state.stage_state.substage_state.sector

        cost = spice_cost(new_game_state, "guild", len(units), space)

        discard_karama(new_game_state, self.faction)

        ship_units(new_game_state, self.faction, units, space, sector)
        spend_spice(new_game_state, self.faction, cost, "shipment-payment")
        new_game_state.karama_context[self.faction] = None

        return new_game_state


class PayShipment(Action):
    name = "pay-shipment"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.substage_state.subsubstage != "pay":
            raise IllegalAction("Wrong subsubstage yo")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.subsubstage = "guide"

        units = new_game_state.round_state.stage_state.substage_state.units
        s = new_game_state.round_state.stage_state.substage_state.space
        space = new_game_state.map_state[s]
        sector = new_game_state.round_state.stage_state.substage_state.sector

        cost = spice_cost(new_game_state, self.faction, len(units), space)
        if cost > new_game_state.faction_state[self.faction].spice:
            raise BadCommand("You cannot pay full price for this shipment")

        ship_units(new_game_state, self.faction, units, space, sector)
        spend_spice(new_game_state, self.faction, cost, "shipment-payment")
        if self.faction != "guild":
            if "guild" in new_game_state.faction_state:
                new_game_state.faction_state["guild"].spice += cost

        return new_game_state


class SendSpiritualAdvisor(Action):
    name = "send-spiritual-advisor"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"
    ck_faction = "bene-gesserit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "guide":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn == "bene-gesserit":
            raise IllegalAction("No guiding yourself guild")
        if not game_state.faction_state["bene-gesserit"].reserve_units:
            raise IllegalAction("You need units to send as advisors")
        space_name = game_state.round_state.stage_state.substage_state.space
        space = game_state.map_state[space_name]
        if "bene-gesserit" in space.forces and not space.coexist:
            raise IllegalAction("You cannot send a spiritual advisor where you have fighters") 

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.subsubstage = "halt-guide"
        return new_game_state


class PassSendSpiritualAdvisor(Action):
    name = "pass-send-spiritual-advisor"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"
    ck_faction = "bene-gesserit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "guide":
            raise IllegalAction("Wrong subsubstage yo")
        if game_state.round_state.faction_turn == "bene-gesserit":
            raise IllegalAction("No guiding yourself guild")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.shipment_used = True
        new_game_state.round_state.stage_state.substage_state = movement.MainSubStage()
        return new_game_state


class SkipSendSpiritualAdvisor(Action):
    name = "skip-send-spiritual-advisor"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "guide":
            raise IllegalAction("Wrong subsubstage yo")
        if "bene-gesserit" in game_state.faction_state:
            if game_state.faction_state["bene-gesserit"].reserve_units:
                if game_state.round_state.faction_turn != "bene-gesserit":
                    space_name = game_state.round_state.stage_state.substage_state.space
                    space = game_state.map_state[space_name]
                    if ("bene-gesserit" not in space.forces) or space.coexist:
                        raise IllegalAction("Cannot auto skip spiritual guide")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.shipment_used = True
        new_game_state.round_state.stage_state.substage_state = movement.MainSubStage()
        return new_game_state


class KarmaStopSpiritualAdvisor(Action):
    name = "karama-stop-spiritual-advisor"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"
    ck_karama = True

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt-guide":
            raise IllegalAction("Wrong subsubstage yo")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        discard_karama(new_game_state, self.faction)
        new_game_state.round_state.stage_state.shipment_used = True
        new_game_state.round_state.stage_state.substage_state = movement.MainSubStage()
        return new_game_state


class KarmaPassStopSpiritualAdvisor(Action):
    name = "karama-pass-stop-spiritual-advisor"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"

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
        space.coexist = True
        if "bene-gesserit" not in space.forces:
            space.forces["bene-gesserit"] = {}
        if sector not in space.forces["bene-gesserit"]:
            space.forces["bene-gesserit"][sector] = []
        u = new_game_state.faction_state["bene-gesserit"].reserve_units.pop(0)
        space.forces["bene-gesserit"][sector].append(u)
        new_game_state.round_state.stage_state.shipment_used = True
        new_game_state.round_state.stage_state.substage_state = movement.MainSubStage()
        return new_game_state


def parse_movement_args(args):
    parts = args.split(" ")
    if len(parts) == 5:
        units, space_a, sector_a, space_b, sector_b = parts
    else:
        raise BadCommand("wrong number of args")

    if units == "":
        raise BadCommand("No units selected")
    units = [int(u) for u in units.split(",")]
    return (units, space_a, int(sector_a), space_b, int(sector_b))


def perform_movement(game_state, faction, units, space_a, sector_a, space_b, sector_b):
    m = MapGraph()
    if faction == "fremen":
        m.deadend_sector(game_state.storm_position)
    else:
        m.remove_sector(game_state.storm_position)
    for space in game_state.map_state.values():
        if "stronghold" in space.type:
            if faction not in space.forces:
                if len(space.forces) - (1 if space.coexist else 0) > 1:
                    m.remove_space(space.name)

    allowed_distance = 1
    if faction == "fremen":
        allowed_distance = 2
    if faction in game_state.ornithopters:
        allowed_distance = 3
    if m.distance(space_a, sector_a, space_b, sector_b) > allowed_distance:
        raise BadCommand("You cannot move there")

    space_a = game_state.map_state[space_a]
    space_b = game_state.map_state[space_b]
    move_units(game_state, faction, units, space_a, sector_a, space_b,
               sector_b)


class Move(Action):
    name = "move"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def parse_args(cls, faction, args):
        return Move(faction, *parse_movement_args(args))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Units(faction), args.SpaceSectorStart(), args.SpaceSectorEnd())

    def __init__(self, faction, units, space_a, sector_a, space_b, sector_b):
        self.faction = faction
        self.units = units
        self.space_a = space_a
        self.space_b = space_b
        self.sector_a = sector_a
        self.sector_b = sector_b

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.movement_used:
            raise IllegalAction("You have already moved this turn")

    def _execute(self, game_state):

        new_game_state = deepcopy(game_state)
        perform_movement(new_game_state,
                         self.faction,
                         self.units,
                         self.space_a,
                         self.sector_a,
                         self.space_b,
                         self.sector_b)
        new_game_state.round_state.stage_state.movement_used = True

        return new_game_state


class CrossShip(Action):
    name = "cross-ship"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 5:
            units, space_a, sector_a, space_b, sector_b = parts
        else:
            raise BadCommand("wrong number of args")

        units = [int(u) for u in units.split(",")]
        sector_a = int(sector_a)
        sector_b = int(sector_b)
        return CrossShip(faction, units, space_a, sector_a, space_b, sector_b)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Units(faction), args.SpaceSectorStart(), args.SpaceSectorEnd())

    def __init__(self, faction, units, space_a, sector_a, space_b, sector_b):
        self.faction = faction
        self.units = units
        self.space_a = space_a
        self.space_b = space_b
        self.sector_a = sector_a
        self.sector_b = sector_b

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        cls.check_alliance(game_state, faction, "guild")
        if game_state.round_state.stage_state.shipment_used:
            raise IllegalAction("You have already shipped this turn")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.ship_has_sailed = True

        space_a = new_game_state.map_state[self.space_a]
        space_b = new_game_state.map_state[self.space_b]
        cost = spice_cost(new_game_state, self.faction, len(self.units), space_b)
        if new_game_state.faction_state[self.faction].spice < cost:
            raise BadCommand("You don't have enough spice")
        spend_spice(new_game_state, self.faction, cost)

        if self.faction != "guild":
            if "guild" in new_game_state.faction_state:
                new_game_state.faction_state["guild"] += cost
        move_units(new_game_state, self.faction, self.units, space_a, self.sector_a, space_b, self.sector_b)

        new_game_state.round_state.stage_state.shipment_used = True

        return new_game_state


class ReverseShip(Action):
    name = "reverse-ship"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 3:
            units, space, sector = parts
        else:
            raise BadCommand("wrong number of args")

        units = [int(u) for u in units.split(",")]
        sector = int(sector)
        return ReverseShip(faction, units, space, sector)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Units(faction), args.SpaceSector())

    def __init__(self, faction, units, space, sector):
        self.faction = faction
        self.units = units
        self.space = space
        self.sector = sector

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        cls.check_alliance(game_state, faction, "guild")
        if game_state.round_state.stage_state.shipment_used:
            raise IllegalAction("You have already shipped this turn")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.ship_has_sailed = True
        if self.sector == new_game_state.storm_position:
            raise BadCommand("You cannot ship out of the storm")

        space = new_game_state.map_state[self.space]
        cost = math.ceil(len(self.units)/2)
        if new_game_state.faction_state[self.faction].spice < cost:
            raise BadCommand("You don't have enough spice")

        spend_spice(new_game_state, self.faction, cost)

        if self.faction != "guild":
            if "guild" in new_game_state.faction_state:
                new_game_state.faction_state["guild"] += cost
        for u in self.units:
            if u not in space.forces[self.faction][self.sector]:
                raise BadCommand("That unit isn't even there!")
            space.forces[self.faction][self.sector].remove(u)
            new_game_state.faction_state[self.faction].reserve_units.append(u)

        new_game_state.round_state.stage_state.shipment_used = True

        return new_game_state


class Deploy(Action):
    name = "deploy"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"
    ck_faction = "fremen"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 3:
            units, space, sector = parts
        else:
            raise BadCommand("wrong number of args")

        units = [int(u) for u in units.split(",")]
        sector = int(sector)
        return Deploy(faction, units, space, sector)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Units(faction), args.SpaceSector())

    def __init__(self, faction, units, space, sector):
        self.faction = faction
        self.units = units
        self.space = space
        self.sector = sector

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.shipment_used:
            raise IllegalAction("You have already shipped this turn")

    def _execute(self, game_state):

        new_game_state = deepcopy(game_state)
        new_game_state.round_state.ship_has_sailed = True
        m = MapGraph()
        if m.distance("The-Great-Flat", 14, self.space, self.sector) > 2:
            raise BadCommand("You cannot deploy there")

        space = new_game_state.map_state[self.space]
        ship_units(new_game_state, self.faction, self.units, space, self.sector)

        new_game_state.round_state.stage_state.shipment_used = True

        return new_game_state
