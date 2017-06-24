from copy import deepcopy
import math

from dune.actions.action import Action
from dune.actions import storm
from dune.exceptions import IllegalAction, BadCommand
from dune.state.rounds import movement, battle
from dune.map.map import MapGraph


def ship_units(game_state, faction, units, space, sector, coexist=False):
    if "stronghold" in space.type:
        if len(space.forces) > 1:
            if faction not in space.forces:
                if not coexist:
                    raise BadCommand("Cannot ship into stronghold with 2 enemy factions")
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


def move_units(game_state, faction, units, space_a, sector_a, space_b, sector_b, coexist=False):
    if "stronghold" in space_b.type:
        if len(space_b.forces) > 1:
            if faction not in space_b.forces:
                if not coexist:
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
    if "bene-gesserit" not in space_a.forces:
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

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "guild":
            raise IllegalAction("The guild cannot do that")
        if faction in game_state.round_state.stage_state.karama_passes:
            raise IllegalAction("You have already passed this option")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You need a karama card to block guild turn choice")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.guild_choice_blocked = True
        faction_order = storm.get_faction_order(game_state)
        new_game_state.round_state.faction_turn = faction_order[0]
        new_game_state.round_state.turn_order = faction_order
        new_game_state.round_state.stage_state = movement.CoexistStage()
        new_game_state.faction_state[self.faction].treachery.remove("Karama")
        new_game_state.treachery_discard.insert(0, "Karama")
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
        faction_order = storm.get_faction_order(game_state)
        if "guild" in faction_order:
            faction_order.remove("guild")
            faction_order.insert(0, "guild")
        new_game_state.round_state.turn_order = faction_order
        new_game_state.round_state.faction_turn = faction_order[0]
        new_game_state.round_state.stage_state = movement.CoexistStage()
        return new_game_state


class CoexistPlace(Action):
    name = "coexist-place"
    ck_round = "movement"
    ck_stage = "coexist"
    ck_faction = "bene-gesserit"

    @classmethod
    def parse_args(cls, faction, args):
        spaces = args.split(" ")
        return CoexistPlace(faction, spaces)

    def __init__(self, faction, spaces):
        self.faction = faction
        self.spaces = spaces

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for s in self.spaces:
            space = new_game_state.map_state[s]
            if "bene-gesserit" not in space.forces:
                raise BadCommand("No forces to coexist")
            space.coexist = True

        new_game_state.round_state.stage_state = movement.TurnStage()
        return new_game_state


class CoexistPersist(Action):
    name = "coexist-persist"
    ck_round = "movement"
    ck_stage = "coexist"
    ck_faction = "bene-gesserit"

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for s in new_game_state.map_state:
            space = new_game_state.map_state[s]
            if "bene-gesserit" in space.forces:
                space.coexist = space.was_coexist

        new_game_state.round_state.stage_state = movement.TurnStage()
        return new_game_state


class SkipCoexist(Action):
    name = "coexist-skip"
    ck_round = "movement"
    ck_stage = "coexist"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "bene-gesserit" in game_state.faction_state:
            raise IllegalAction("Cannot skip coexist if bene-gesserit are present")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
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
            coexist = False
        elif len(parts) == 4:
            units, space, sector, coexist = parts
            coexist = coexist == "coexist"
        else:
            raise BadCommand("Shipment Requires Different Arguments")

        units = [int(i) for i in units.split(",")]
        sector = int(sector)

        return Ship(faction, units, space, sector, coexist)

    def __init__(self, faction, units, space, sector, coexist):
        self.faction = faction
        self.units = units
        self.space = space
        self.sector = sector
        self.coexist = coexist

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if faction == "fremen":
            raise IllegalAction("Fremen cannot ship")
        if game_state.round_state.stage_state.shipment_used:
            raise IllegalAction("You have already shipped this turn")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)


        space = new_game_state.map_state[self.space]
        if self.sector not in space.sectors:
            raise BadCommand("That sector is not in that space")
        if new_game_state.storm_position == self.sector:
            if self.faction != "fremen":
                raise BadCommand("Only the Fremen can ship into the storm")

        min_cost = spice_cost(new_game_state, self.faction, len(self.units), space)

        if "Karama" in new_game_state.faction_state[self.faction].treachery:
            min_cost = spice_cost(new_game_state, "guild", len(self.units), space)
        if new_game_state.faction_state[self.faction].spice < min_cost:
            raise BadCommand("Insufficient spice for this shipment")

        new_game_state.round_state.stage_state.substage_state = movement.ShipSubStage()
        new_game_state.round_state.stage_state.substage_state.units = self.units
        new_game_state.round_state.stage_state.substage_state.space = self.space
        new_game_state.round_state.stage_state.substage_state.sector = self.sector
        new_game_state.round_state.stage_state.substage_state.coexist = self.coexist

        return new_game_state


class KaramaStopShipment(Action):
    name = "karama-stop-shipment"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "ship"
    ck_faction = "guild"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt":
            raise IllegalAction("Wrong subsubstage yo")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You need a Karama card to do this")
        if game_state.round_state.faction_turn == "guild":
            raise IllegalAction("No stopping yourself guild")

    def _execute(self, game_state, faction):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.shipment_used = True
        new_game_state.round_state.stage_state.substage = movement.MainSubStage()
        new_game_state.faction_state[self.faction].treachery.remove("Karama")
        new_game_state.treachery_discard.insert(0, "Karama")
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

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if "Karma" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You need a karama card to do that")
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
        coexist = new_game_state.round_state.stage_state.substage_state.coexist

        cost = spice_cost(new_game_state, "guild", len(units), space)

        new_game_state.faction_state[self.faction].treachery.remove("Karama")
        new_game_state.treachery_discard.insert(0, "Karama")

        ship_units(new_game_state, self.faction, units, space, sector)
        new_game_state.faction_state[self.faction].spice -= cost
        space.coexist = coexist

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
        coexist = new_game_state.round_state.stage_state.substage_state.coexist

        cost = spice_cost(new_game_state, self.faction, len(units), space)
        if cost > new_game_state.faction_state[self.faction].spice:
            raise BadCommand("You cannot pay full price for this shipment")

        ship_units(new_game_state, self.faction, units, space, sector)
        new_game_state.faction_state[self.faction].spice -= cost
        if self.faction != "guild":
            if "guild" in new_game_state.faction_state:
                new_game_state.faction_state["guild"].spice += cost
        space.coexist = coexist

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

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.substage_state.subsubstage != "halt-guide":
            raise IllegalAction("Wrong subsubstage yo")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You need a Karama card")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.faction_state[self.faction].treachery.remove("Karama")
        new_game_state.treachery_discard.insert(0, "Karama")
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


class Move(Action):
    name = "move"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 5:
            units, space_a, sector_a, space_b, sector_b = parts
            coexist = False
        elif len(parts) == 6:
            units, space_a, sector_a, space_b, sector_b, coexist = parts
            coexist = coexist == "coexist"
        else:
            raise BadCommand("wrong number of args")

        if coexist and faction != "bene-gesserit":
            raise BadCommand("Only the bene-gesserit may coexist")

        units = [int(u) for u in units.split(",")]
        sector_a = int(sector_a)
        sector_b = int(sector_b)
        return Move(faction, units, space_a, sector_a, space_b, sector_b, coexist)

    def __init__(self, faction, units, space_a, sector_a, space_b, sector_b, coexist):
        self.faction = faction
        self.units = units
        self.space_a = space_a
        self.space_b = space_b
        self.sector_a = sector_a
        self.sector_b = sector_b
        self.coexist = coexist

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.movement_used:
            raise IllegalAction("You have already moved this turn")

    def _execute(self, game_state):

        new_game_state = deepcopy(game_state)
        m = MapGraph()
        if self.faction == "fremen":
            m.deadend_sector(new_game_state.storm_position)
        else:
            m.remove_sector(new_game_state.storm_position)
        for space in new_game_state.map_state.values():
            if "stronghold" in space.type:
                if self.faction not in space.forces:
                    if len(space.forces) - (1 if space.coexist else 0) > 1:
                        m.remove_space(space.name)

        allowed_distance = 1
        if self.faction == "fremen":
            allowed_distance = 2
        if self.faction in new_game_state.ornithopters:
            allowed_distance = 3
        if m.distance(self.space_a, self.sector_a, self.space_b, self.sector_b) > allowed_distance:
            raise BadCommand("You cannot move there")

        space_a = new_game_state.map_state[self.space_a]
        space_b = new_game_state.map_state[self.space_b]
        move_units(new_game_state, self.faction, self.units, space_a, self.sector_a, space_b,
                   self.sector_b, self.coexist and self.faction == "bene-gesserit")

        if self.coexist and self.faction == "bene-gesserit":
            space_b.coexist = True

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
        if len(parts) == 6:
            units, space_a, sector_a, space_b, sector_b, coexist = parts
            coexist = coexist == "coexist"
        elif len(parts) == 5:
            units, space_a, sector_a, space_b, sector_b = parts
            coexist = False
        else:
            raise BadCommand("wrong number of args")

        units = [int(u) for u in units.split(",")]
        sector_a = int(sector_a)
        sector_b = int(sector_b)
        return CrossShip(faction, units, space_a, sector_a, space_b, sector_b, coexist)

    def __init__(self, faction, units, space_a, sector_a, space_b, sector_b, coexist):
        self.faction = faction
        self.units = units
        self.space_a = space_a
        self.space_b = space_b
        self.sector_a = sector_a
        self.sector_b = sector_b
        self.coexist = coexist

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        cls.check_alliance(game_state, faction, "guild")
        if game_state.round_state.stage_state.shipment_used:
            raise IllegalAction("You have already shipped this turn")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        space_a = new_game_state.map_state[self.space_a]
        space_b = new_game_state.map_state[self.space_b]
        cost = spice_cost(new_game_state, self.faction, len(self.units), space_b)
        if new_game_state.faction_state[self.faction].spice < cost:
            raise BadCommand("You don't have enough spice")
        new_game_state.faction_state[self.faction].spice -= cost
        if self.faction != "guild":
            if "guild" in new_game_state.faction_state:
                new_game_state.faction_state["guild"] += cost
        move_units(new_game_state, self.faction, self.units, space_a, self.sector_a, space_b, self.sector_b,
                   self.coexist and self.faction == "bene-gesserit")

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
        if self.sector == new_game_state.storm_position:
            raise BadCommand("You cannot ship out of the storm")

        space = new_game_state.map_state[self.space]
        cost = math.ceil(len(self.units)/2)
        if new_game_state.faction_state[self.faction].spice < cost:
            raise BadCommand("You don't have enough spice")
        new_game_state.faction_state[self.faction].spice -= cost
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
        m = MapGraph()
        if m.distance("Great-Flat", 14, self.space, self.sector) > 2:
            raise BadCommand("You cannot deploy there")

        space = new_game_state.map_state[self.space]
        ship_units(new_game_state, self.faction, self.units, space, self.sector)

        new_game_state.round_state.stage_state.shipment_used = True

        return new_game_state
