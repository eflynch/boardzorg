import React from 'react';

import Card from '../components/card';
import FactionOrder from '../components/faction-order';



class Retrieval extends React.Component {
    render () {
        let {roundState, factionOrder} = this.props;
        let turnOrder = <FactionOrder factions={factionOrder.map((faction)=>{
            return {
                faction: faction,
                active: faction === roundState.faction_turn
            };
        })} />;
        return (
            <div style={{display:"flex", flexDirection:"column"}}>
                {turnOrder}
            </div>
        );
    }
}

module.exports = Retrieval;
