from copy import deepcopy

from boardzorg.actions.action import Action
from boardzorg.actions.common import get_faction_order
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.state.rounds.retrieval import RetrievalRound
from boardzorg.state.rounds import bidding
from boardzorg.actions import args
from boardzorg.actions.author import discard_author
from boardzorg.actions.hunny import spend_hunny


def next_bidder(game_state):
    faction_order = get_faction_order(game_state)
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
    faction_order = get_faction_order(game_state)
    faction_index = game_state.round_state.total_for_auction - len(game_state.round_state.up_for_auction)
    return faction_order[faction_index % len(faction_order)]


def do_payment(game_state):
    winner = game_state.round_state.stage_state.winner
    bid = game_state.round_state.stage_state.winning_bid
    spend_hunny(game_state, winner, bid, "payment")
    if winner != "eeyore" and "eeyore" in game_state.faction_state:
        game_state.faction_state["eeyore"].hunny += bid
    card = game_state.round_state.up_for_auction.pop(0)
    game_state.faction_state[winner].provisions.append(card)

    return game_state


class ChoamCharity(Action):
    name = "choam-charity"
    ck_round = "bidding"

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if faction not in game_state.round_state.choam_claimers:
            raise IllegalAction("CHOAM Charity is only for the poor and meek")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.faction_state[self.faction].hunny += game_state.round_state.choam_claimers[self.faction]
        del new_game_state.round_state.choam_claimers[self.faction]
        return new_game_state


class StartAuction(Action):
    name = "start-auction"
    ck_round = "bidding"
    ck_stage = "setup"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for i in range(len(new_game_state.faction_state)):
            if new_game_state.provisions_deck:
                c = new_game_state.provisions_deck.pop(0)
                new_game_state.round_state.up_for_auction.append(c)

        for faction in new_game_state.faction_state:
            if faction == "rabbit":
                new_game_state.round_state.choam_claimers[faction] = 2
            elif new_game_state.faction_state[faction].hunny < 2:
                new_game_state.round_state.choam_claimers[faction] = 2 - new_game_state.faction_state[faction].hunny

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
            hunny = float("inf")
        else:
            hunny = int(args)
        return Bid(faction, hunny)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Union(args.Constant("inf"), args.Hunny())

    def __init__(self, faction, hunny):
        self.faction = faction
        self.hunny = hunny

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.substage_state.faction_turn != faction:
            raise IllegalAction("It's not your turn")
        if faction in game_state.round_state.stage_state.bids:
            if game_state.round_state.stage_state.bids[faction] == "pass":
                raise IllegalAction("Cannot bid again once passed")

        if len(game_state.faction_state[faction].provisions) > 7:
            raise IllegalAction("You cannot bid with this many provisions cards")

        if faction != "piglet" and len(game_state.faction_state[faction].provisions) > 3:
            raise IllegalAction("You cannot bid with this many provisions cards")

    def _execute(self, game_state):
        highest = max([0] + [v for v in game_state.round_state.stage_state.bids.values() if v != "pass"])
        if self.hunny <= highest:
            raise BadCommand("Must bid higher than the highest bid")

        new_game_state = deepcopy(game_state)

        # WEIRD PATTERN ALERT
        class LocalException(Exception):
            pass

        try:
            self.check_author(game_state, self.faction, LocalException)
            reserve_hunny = None
        except LocalException:
            reserve_hunny = self.hunny

        # END ALERT

        new_game_state.hunny_reserve[self.faction] = reserve_hunny
        if reserve_hunny is not None:
            new_game_state.hunny_context[self.faction] = "payment"

        if self.hunny > game_state.faction_state[self.faction].hunny:
            self.check_author(game_state, self.faction, BadCommand("Must not bid higher than you have hunny"))
            new_game_state.author_context[self.faction] = "payment"

        new_game_state.round_state.stage_state.bids[self.faction] = self.hunny
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
        new_game_state.author_context[self.faction] = None
        new_game_state.hunny_context[self.faction] = None
        new_game_state.hunny_reserve[self.faction] = None
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
        new_game_state.pause_context = "payment"
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
                new_game_state.provisions_deck.insert(0, card)

        new_game_state.round_state = RetrievalRound()
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
        new_game_state.round_state = RetrievalRound()
        return new_game_state


class AuthorFreeBid(Action):
    name = "author-free-bid"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "payment"
    ck_author = True
    ck_author_context = ["payment"]
    ck_pause_context = ["payment"]

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.winner:
            raise IllegalAction("You need to be the winner first")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        discard_author(new_game_state, self.faction)
        card = new_game_state.round_state.up_for_auction.pop(0)
        new_game_state.faction_state[self.faction].provisions.append(card)

        new_game_state.round_state.stage_state.substage_state = bidding.CollectSubStage()
        new_game_state.pause_context = None
        new_game_state.author_context[self.faction] = None

        return new_game_state


class Pay(Action):
    name = "pay-bid"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "payment"
    ck_pause_context = ["payment"]

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.winner:
            raise IllegalAction("You need to be the winner first")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        do_payment(new_game_state)
        new_game_state.round_state.stage_state.substage_state = bidding.CollectSubStage()
        new_game_state.pause_context = None

        return new_game_state


class SkipCollect(Action):
    name = "skip-collect"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "collect"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.winner == "piglet":
            if game_state.provisions_deck and len(game_state.faction_state["piglet"].provisions) < 8:
                raise IllegalAction("Cannot skip collection because the Piglet can collect")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state = bidding.AuctionStage()
        new_game_state.round_state.stage_state.substage_state.faction_turn = next_first_bidder(new_game_state)
        return new_game_state


class AuthorStopExtra(Action):
    name = "author-stop-extra"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "collect"
    ck_author = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "piglet":
            raise IllegalAction("Can't karam your own deal")
        if game_state.round_state.stage_state.winner != "piglet":
            raise IllegalAction("This only matters to the piglet")
        if not game_state.provisions_deck:
            raise IllegalAction("No more cards anyways")
        if len(game_state.faction_state["piglet"].provisions) >= 8:
            raise IllegalAction("The piglet have no room for a new card")
        if faction in game_state.round_state.stage_state.substage_state.author_passes:
            raise IllegalAction("You've already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state = bidding.AuctionStage()
        new_game_state.round_state.stage_state.substage_state.faction_turn = next_first_bidder(new_game_state)
        discard_author(new_game_state, self.faction)
        return new_game_state


class AuthorPassStopExtra(Action):
    name = "author-pass-stop-extra"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "collect"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "piglet":
            raise IllegalAction("Can't karam your own deal")
        if game_state.round_state.stage_state.winner != "piglet":
            raise IllegalAction("This only matters to the piglet")
        if not game_state.provisions_deck:
            raise IllegalAction("No more cards anyways")
        if len(game_state.faction_state["piglet"].provisions) >= 8:
            raise IllegalAction("The piglet have no room for a new card")
        if faction in game_state.round_state.stage_state.substage_state.author_passes:
            raise IllegalAction("You've already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.author_passes.append(self.faction)
        return new_game_state


class ResolveCollect(Action):
    name = "resolve-collect"
    ck_round = "bidding"
    ck_stage = "auction"
    ck_substage = "collect"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.winner != "piglet":
            raise IllegalAction("Don't collect if Piglet didn't win")

        if not game_state.provisions_deck or len(game_state.faction_state["piglet"].provisions) == 8:
            raise IllegalAction("The Piglet cannot collect anyway")

        if len(game_state.round_state.stage_state.substage_state.author_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Waiting for author passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        card = new_game_state.provisions_deck.pop(0)
        new_game_state.faction_state["piglet"].provisions.append(card)
        new_game_state.round_state.stage_state = bidding.AuctionStage()
        new_game_state.round_state.stage_state.substage_state.faction_turn = next_first_bidder(new_game_state)
        return new_game_state
