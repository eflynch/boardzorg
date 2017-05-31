from copy import deepcopy

from exceptions import IllegalAction

from actions.action import Action
from actions.setup import TOKEN_SECTORS

from state.state import RevivalState


def get_faction_order(game_state):
    faction_order = []
    storm_position = game_state.board_state.storm_position
    for i in range(18):
        sector = (storm_position + i + 1) % 18
        if sector in TOKEN_SECTORS:
            for f in game_state.faction_state:
                faction_state = game_state.faction_state[f]
                if faction_state.token_position == sector:
                    faction_order.append(f)
    return faction_order


def next_bidder(game_state):
    faction_order = get_faction_order(game_state)
    turn_index = faction_order.index(game_state.round_state.faction_turn)
    for i in range(6):
        next_bidder_candidate = faction_order[(turn_index + 1 + i) % 6]
        if next_bidder_candidate not in game_state.round_state.bids:
            return next_bidder_candidate
        if game_state.round_state.bids[next_bidder_candidate] != "pass":
            return next_bidder_candidate
    return None


def next_first_bidder(game_state):
    faction_order = get_faction_order(game_state)
    faction_index = game_state.round_state.total_for_auction - len(game_state.round_state.up_for_auction)
    return faction_order[faction_index]


class ChoamCharity(Action):
    name = "choam-charity"
    ck_round = "bidding"

    @classmethod
    def parse_args(cls, faction, args):
        return ChoamCharity(faction)

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
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.faction_turn is not None:
            raise IllegalAction("Auction already started")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for i in range(6):
            if new_game_state.treachery_deck:
                c = new_game_state.treachery_deck.pop(0)
                new_game_state.round_state.up_for_auction.append(c)
        new_game_state.round_state.faction_turn = next_first_bidder(new_game_state)
        new_game_state.round_state.total_for_auction = len(new_game_state.round_state.up_for_auction)
        return new_game_state


class Bid(Action):
    name = "bid"
    ck_round = "bidding"

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
        cls.check_turn(game_state, faction)
        if faction in game_state.round_state.bids:
            if game_state.round_state.bids[faction] == "pass":
                raise IllegalAction("Cannot bid again once passed")

        if len(game_state.faction_state[faction].treachery) > 7:
            raise IllegalAction("You cannot bid with this many treachery cards")

        if faction != "harkonnen" and len(game_state.faction_state[faction].treachery) > 3:
            raise IllegalAction("You cannot bid with this many treachery cards")

    def _execute(self, game_state):
        highest = max([0] + [v for v in game_state.round_state.bids.values() if v != "pass"])
        if self.spice <= highest:
            raise IllegalAction("Must bid higher than the highest bid")

        if self.spice > game_state.faction_state[self.faction].spice:
            if "Karama" not in game_state.faction_state[self.faction].treachery:
                raise IllegalAction("Must not bid higher than you have spice")

        new_game_state = deepcopy(game_state)
        new_game_state.round_state.bids[self.faction] = self.spice
        new_game_state.round_state.faction_turn = next_bidder(new_game_state)

        return new_game_state


class Pass(Action):
    name = "pass"
    ck_round = "bidding"

    @classmethod
    def parse_args(cls, faction, args):
        return Pass(faction)

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)

    def execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.bids[self.faction] = "pass"
        new_game_state.round_state.faction_turn = next_bidder(new_game_state)
        return new_game_state


class KaramaFreeBid(Action):
    name = "karama-free-bid"
    ck_round = "bidding"

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.round_state.winner:
            raise IllegalAction("You need to win the bid first")
        if faction != game_state.round_state.winner:
            raise IllegalAction("You need to be the winner first")
        if game_state.round_state.payment_done:
            raise IllegalAction("Already payed for this")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You don't have a karama card")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.faction_state[self.faction].treachery.remove("Karama")
        new_game_state.treachery_discard.insert(0, "Karama")
        card = new_game_state.round_state.up_for_auction.pop(0)
        new_game_state.faction_state[self.faction].treachery.append(card)
        new_game_state.round_state.payment_done = True

        return new_game_state


class KaramaPassFreeBid(Action):
    name = "karama-pass-free-bid"
    ck_round = "bidding"

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.round_state.winner:
            raise IllegalAction("You need to win the bid first")
        if faction != game_state.round_state.winner:
            raise IllegalAction("You need to be the winner to bother with this")
        if game_state.round_state.payment_done:
            raise IllegalAction("Already payed for this")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You don't have a karama card anyways")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.payment_cancel_passed = True

        return new_game_state


class KaramaStopExtra(Action):
    name = "karama-stop-extra"
    ck_round = "bidding"

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.round_state.payment_done:
            raise IllegalAction("Wait till that shit's payed for")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You don't have a karama card anyways")
        if game_state.round_state.winner != "harkonnen":
            raise IllegalAction("This only matters to the harkonnen")
        if not game_state.treachery_deck:
            raise IllegalAction("No more cards anyways")
        if len(game_state.faction_state["harkonnen"].treachery) >= 8:
            raise IllegalAction("The harkonnen have no room for a new card")
        if faction in game_state.round_state.karama_passes:
            raise IllegalAction("You've already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.extra_card_karama_used = True
        return new_game_state


class KaramPassStopExtra(Action):
    name = "karama-pass-stop-extra"
    ck_round = "bidding"

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.round_state.payment_done:
            raise IllegalAction("Wait till that shit's payed for")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You don't have a karama card anyways")
        if game_state.round_state.winner != "harkonnen":
            raise IllegalAction("This only matters to the harkonnen")
        if not game_state.treachery_deck:
            raise IllegalAction("No more cards anyways")
        if len(game_state.faction_state["harkonnen"].treachery) >= 8:
            raise IllegalAction("The harkonnen have no room for a new card")
        if faction in game_state.round_state.karama_passes:
            raise IllegalAction("You've already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.karama_passes.append(self.faction)
        return new_game_state


class ResolveWinner(Action):
    name = "resolve-winner"
    ck_round = "bidding"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.bids) != 6:
            raise IllegalAction("Not everyone has bid")

        if list(game_state.round_state.bids.values()).count("pass") < 5:
            raise IllegalAction("Not everyone has passed")

        if list(game_state.round_state.bids.values()).count("pass") != 5:
            raise IllegalAction("No bid to resolve")

        if game_state.round_state.winner:
            raise IllegalAction("Winner already resolved")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for f in new_game_state.round_state.bids:
            bid = new_game_state.round_state.bids[f]
            if bid != "pass":
                winner = f
                break

        new_game_state.round_state.winner = winner

        if new_game_state.faction_state[winner].spice < bid:
            new_game_state.faction_state[winner].treachery.remove("Karama")
            new_game_state.treachery_discard.insert(0, "Karama")
            card = new_game_state.round_state.up_for_auction.pop(0)
            new_game_state.faction_state[winner].treachery.append(card)
            new_game_state.round_state.payment_done = True

        return new_game_state


class ResolvePayment(Action):
    name = "resolve-payment"
    ck_round = "bidding"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.round_state.winner:
            raise IllegalAction("No winner determined")
        if game_state.round_state.payment_done:
            raise IllegalAction("Already Payed")
        if "Karama" in game_state.faction_state[game_state.round_state.winner].treachery:
            if not game_state.round_state.payment_cancel_passed:
                raise IllegalAction("Waiting for karama pass")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        winner = new_game_state.round_state.winner
        bid = new_game_state.round_state.bids[winner]

        new_game_state.faction_state[winner].spice -= bid
        if winner != "emperor":
            new_game_state.faction_state["emperor"].spice += bid

        card = new_game_state.round_state.up_for_auction.pop(0)
        new_game_state.faction_state[winner].treachery.append(card)
        new_game_state.round_state.payment_done = True

        return new_game_state


class ResolveBid(Action):
    name = "resolve-bid"
    ck_round = "bidding"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.round_state.payment_done:
            raise IllegalAction("Waiting for payment")
        if game_state.round_state.winner == "harkonnen":
            if game_state.treachery_deck and len(game_state.faction_state["harkonnen"].treachery) < 8:
                if not game_state.round_state.extra_card_karama_used and len(game_state.round_state.karama_passes) != 5:
                    raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        winner = new_game_state.round_state.winner

        if winner == "harkonnen":
            if new_game_state.treachery_deck and len(new_game_state.faction_state["harkonnen"].treachery) < 8:
                if not game_state.round_state.extra_card_karama_used:
                    card = new_game_state.treachery_deck.pop(0)
                    new_game_state.faction_state["harkonnen"].treachery.append(card)

        new_game_state.round_state.faction_turn = next_first_bidder(new_game_state)
        new_game_state.round_state.bids = {}
        new_game_state.round_state.payment_done = False
        new_game_state.round_state.payment_cancel_passed = False
        new_game_state.round_state.winner = None
        new_game_state.round_state.payment_cancel_passed = False
        new_game_state.round_state.extra_card_karama_used = False
        new_game_state.round_state.karama_passes = []

        return new_game_state


class EndAuction(Action):
    name = "end-auction"
    ck_round = "bidding"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.faction_turn is None:
            raise IllegalAction("The auction has yet to begin")
        if game_state.round_state.up_for_auction:
            if list(game_state.round_state.bids.values()).count("pass") != 6:
                raise IllegalAction("Items still up for auction and not everyone has passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        if new_game_state.round_state.up_for_auction:
            while new_game_state.round_state.up_for_auction:
                card = new_game_state.round_state.up_for_auction.pop()
                new_game_state.treachery_deck.insert(0, card)

        new_game_state.round_state = RevivalState()
        return new_game_state
