import React from 'react';

import TreacheryCard from '../components/treachery-card';
import FactionOrder from '../components/faction-order';



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
    render () {
        let {roundstate, factionOrder} = this.props;
        let turnOrder = <FactionOrder factions={factionOrder.map((faction)=>{
            return {
                faction: faction,
                label: this.props.roundstate.stage_state.bids[faction],
                active: faction === this.props.roundstate.stage_state.substage_state.faction_turn
            };
        })} />;
        if (roundstate.stage_state.stage === "auction"){
            return (
                <div style={{display:"flex", flexDirection:"column"}}>
                    <h4>Bidding Round</h4>
                    {turnOrder}
                    <div>
                        {this.getCards()}
                    </div>
                </div>
            );
        }
        return <div/>;
    }
}

module.exports = Bidding;