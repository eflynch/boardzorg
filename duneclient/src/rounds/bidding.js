import React from 'react';

import Card from '../components/card';
import FactionOrder from '../components/faction-order';



class Bidding extends React.Component {
    getCards () {
        let cards = [];
        let reverses = this.props.roundstate.up_for_auction.length;
        if (this.props.roundstate.up_for_auction.next !== undefined){
            cards.push(<Card type="Treachery"
                key="next" name={this.props.roundstate.up_for_auction.next}/>);
            reverses -=1;
        }
        for (let i=0; i<reverses;i++){
            cards.push(<Card type="Treachery" key={i} name="Reverse"/>);
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
                    {turnOrder}
                    <div style={{display:"flex", flexWrap:"wrap"}}>
                        {this.getCards()}
                    </div>
                </div>
            );
        }
        return <div/>;
    }
}

module.exports = Bidding;