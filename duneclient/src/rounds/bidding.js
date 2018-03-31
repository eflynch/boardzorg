import React from 'react';

import TreacheryCard from '../components/treachery-card';

class Bidding extends React.Component {
    getCards () {
        let cards = [];
        let reverses = this.props.roundstate.up_for_auction.length;
        if (this.props.roundstate.up_for_auction.next !== undefined){
            cards.push(<TreacheryCard
                key="next" name={this.props.roundstate.up_for_auction.next}/>);
            reverses -=1;
        }
        for (let i=0; i<reverses;i++){
            cards.push(<TreacheryCard key={i} name="Reverse"/>);
        }
        return cards;
    }
    getBids () {
        return Object.keys(this.props.roundstate.stage_state.bids).map((faction) => {
            return (
                <li key={faction}>
                    {faction} : {this.props.roundstate.stage_state.bids[faction]}
                </li>
            );
        });
    }
    render () {
        if (this.props.roundstate.stage_state.stage === "auction"){
            return (
                <div>
                    <h4>Bidding Round</h4>
                    {this.getCards()}
                    {this.getBids()}
                </div>
            );
        }
        return <div/>;
    }
}

module.exports = Bidding;