from copy import deepcopy

from dune.actions import storm
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.state.rounds.revival import RevivalRound
from dune.state.rounds import bidding


def next_bidder(game_state):
    faction_order = storm.get_faction_order(game_state)
    turn_index = faction_order.index(game_state.round_state.stage_state.substage_state.faction_turn)
    num_factions = len(faction_order)
    for i in range(num_factions):
        next_bidder_candidate = faction_order[(turn_index + 1 + i) % num_factions]
        if next_bidder_candidate not in game_state.round_state.stage_state.bids:
            return next_bidder_candidate
        if game_state.round_state.stage_state.bids[next_bidder_candidate] != "pass":
            return next_bidder_candidate
    return None


def next_first_bidder(game_state):
    faction_order = storm.get_faction_order(game_state)
    faction_index = game_state.round_state.total_for_auction - len(game_state.round_state.up_for_auction)
    return faction_order[faction_index]


def do_payment(game_state):
    winner = game_state.round_state.stage_state.winner
    bid = game_state.round_state.stage_state.winning_bid
    game_state.faction_state[winner].spice -= bid
    if winner != "emperor" and "emperor" in game_state.faction_state:
        game_state.faction_state["emperor"].spice += bid
    card = game_state.round_state.up_for_auction.pop(0)
    game_state.faction_state[winner].treachery.append(card)

    return game_state


class ChoamCharity(Action):
    name = "choam-charity"
    ck_round = "bidding"

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if faction != "bene-gesserit" and game_state.faction_state[faction].spice > 0:
            raise IllegalAction("CHOAM Charity is only for the poor and meek")

        if faction == "bene-gesserit" and game_state.round_state.bene_gesserit_charity_claimed:
            raise IllegalAction("CHOAM is generous but not so generous")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.faction_state[self.faction].spice += 2
        if self.faction == "bene-gesserit":
            new_game_state.round_state.bene_gesserit_charity_claimed = True
        return new_game_state


class StartAuction(Action):
    name = "start-auction"
    ck_round = "bidding"
    ck_stage = "setup"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for i in range(len(new_game_state.faction_state)):
            if new_game_state.treachery_deck:
                c = new_game_state.treachery_deck.pop(0)
                new_game_state.round_state.up_for_auction.append(c)
        new_game_state.round_state.total_for_auction = len(new_game_state.round_state.up_for_auction)
        new_game_state.round_state.stage_state = bidding.AuctionStage()
        new_game_state.round_state.stage_state.substage_state.faction_turn = next_first_bidder(new_game_state)
        return new_game_state


class Bid(Action):
    name = "bid"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "bidding"

    @classmethod
    def parse_args(cls, faction, args):
        if args == "inf":
            spice = float("inf")
        else:
            spice = int(args)
        return Bid(faction, spice)

    def __init__(self, faction, spice):
        self.faction = faction
        self.spice = spice

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.faction_turn != faction:
            raise IllegalAction("It's not your turn")
        if faction in game_state.round_state.stage_state.bids:
            if game_state.round_state.stage_state.bids[faction] == "pass":
                raise IllegalAction("Cannot bid again once passed")

        if len(game_state.faction_state[faction].treachery) > 7:
            raise IllegalAction("You cannot bid with this many treachery cards")

        if faction != "harkonnen" and len(game_state.faction_state[faction].treachery) > 3:
            raise IllegalAction("You cannot bid with this many treachery cards")

    def _execute(self, game_state):
        highest = max([0] + [v for v in game_state.round_state.stage_state.bids.values() if v != "pass"])
        if self.spice <= highest:
            raise BadCommand("Must bid higher than the highest bid")

        if self.spice > game_state.faction_state[self.faction].spice:
            if "Karama" not in game_state.faction_state[self.faction].treachery:
                raise BadCommand("Must not bid higher than you have spice")

        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.bids[self.faction] = self.spice
        new_game_state.round_state.stage_state.substage_state.faction_turn = next_bidder(new_game_state)

        return new_game_state


class Pass(Action):
    name = "pass"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "bidding"

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.faction_turn != faction:
            raise IllegalAction("It's not your turn")

    def execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.bids[self.faction] = "pass"
        new_game_state.round_state.stage_state.substage_state.faction_turn = next_bidder(new_game_state)
        return new_game_state


class ResolveWinner(Action):
    name = "resolve-winner"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "bidding"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.stage_state.bids) != len(game_state.faction_state):
            raise IllegalAction("Not everyone has bid")

        if list(game_state.round_state.stage_state.bids.values()).count("pass") < len(game_state.faction_state) - 1:
            raise IllegalAction("Not everyone has passed")

        if list(game_state.round_state.stage_state.bids.values()).count("pass") != len(game_state.faction_state) - 1:
            raise IllegalAction("No bid to resolve")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for f in new_game_state.round_state.stage_state.bids:
            bid = new_game_state.round_state.stage_state.bids[f]
            if bid != "pass":
                winner = f
                break

        new_game_state.round_state.stage_state.substage_state = bidding.PaymentSubStage()
        new_game_state.round_state.stage_state.winner = winner
        new_game_state.round_state.stage_state.winning_bid = bid

        return new_game_state


class PassAuction(Action):
    name = "pass-auction"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "bidding"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if list(game_state.round_state.stage_state.bids.values()).count("pass") != len(game_state.faction_state):
            raise IllegalAction("Items still up for auction and not everyone has passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        if new_game_state.round_state.up_for_auction:
            while new_game_state.round_state.up_for_auction:
                card = new_game_state.round_state.up_for_auction.pop()
                new_game_state.treachery_deck.insert(0, card)

        new_game_state.round_state = RevivalRound()
        return new_game_state


class EndAuction(Action):
    name = "end-auction"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "bidding"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.up_for_auction:
            raise IllegalAction("Items still up for auction")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state = RevivalRound()
        return new_game_state


class KaramaFreeBid(Action):
    name = "karama-free-bid"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "payment"

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.winner:
            raise IllegalAction("You need to be the winner first")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You don't have a karama card")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.faction_state[self.faction].treachery.remove("Karama")
        new_game_state.treachery_discard.insert(0, "Karama")
        card = new_game_state.round_state.up_for_auction.pop(0)
        new_game_state.faction_state[self.faction].treachery.append(card)

        new_game_state.round_state.stage_state.substage_state = bidding.CollectSubStage()

        return new_game_state


class Pay(Action):
    name = "pay-bid"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "payment"

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.winner:
            raise IllegalAction("You need to be the winner first")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        do_payment(new_game_state)
        new_game_state.round_state.stage_state.substage_state = bidding.CollectSubStage()

        return new_game_state


class SkipCollect(Action):
    name = "skip-collect"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "collect"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.winner == "harkonnen":
            if game_state.treachery_deck and len(game_state.faction_state["harkonnen"].treachery) < 8:
                raise IllegalAction("Cannot skip collection because the Harkonnen can collect")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state = bidding.AuctionStage()
        new_game_state.round_state.stage_state.substage_state.faction_turn = next_first_bidder(new_game_state)
        return new_game_state


class KaramaStopExtra(Action):
    name = "karama-stop-extra"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "collect"

    @classmethod
    def _check(cls, game_state, faction):
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You don't have a karama card anyway")
        if game_state.round_state.stage_state.winner != "harkonnen":
            raise IllegalAction("This only matters to the harkonnen")
        if not game_state.treachery_deck:
            raise IllegalAction("No more cards anyways")
        if len(game_state.faction_state["harkonnen"].treachery) >= 8:
            raise IllegalAction("The harkonnen have no room for a new card")
        if faction in game_state.round_state.stage_state.substage_state.karama_passes:
            raise IllegalAction("You've already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state = bidding.AuctionStage()
        new_game_state.round_state.stage_state.substage_state.faction_turn = next_first_bidder(new_game_state)
        return new_game_state


class KaramPassStopExtra(Action):
    name = "karama-pass-stop-extra"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "collect"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.winner != "harkonnen":
            raise IllegalAction("This only matters to the harkonnen")
        if not game_state.treachery_deck:
            raise IllegalAction("No more cards anyways")
        if len(game_state.faction_state["harkonnen"].treachery) >= 8:
            raise IllegalAction("The harkonnen have no room for a new card")
        if faction in game_state.round_state.stage_state.substage_state.karama_passes:
            raise IllegalAction("You've already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.karama_passes.append(self.faction)
        return new_game_state


class ResolveCollect(Action):
    name = "resolve-collect"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "collect"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.winner != "harkonnen":
            raise IllegalAction("Don't collect if Harkonnen didn't win")

        if not game_state.treachery_deck or len(game_state.faction_state["harkonnen"].treachery) == 8:
            raise IllegalAction("The Harkonnen cannot collect anyway")

        if len(game_state.round_state.stage_state.substage_state.karama_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        card = new_game_state.treachery_deck.pop(0)
        new_game_state.faction_state["harkonnen"].treachery.append(card)
        new_game_state.round_state.stage_state = bidding.AuctionStage()
        new_game_state.round_state.stage_state.substage_state.faction_turn = next_first_bidder(new_game_state)
        return new_game_state
