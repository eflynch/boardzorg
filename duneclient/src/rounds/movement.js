import React from 'react';

import FactionOrder from '../components/faction-order';



class Movement extends React.Component {
    render () {
        let {roundstate} = this.props;
        const turnIndex = roundstate.turn_order.indexOf(roundstate.faction_turn);
        let turnOrder = <FactionOrder factions={roundstate.turn_order.map((faction, i)=>{
            return {
                faction: faction,
                label: turnIndex > i ? "done" : "",
                active: faction === roundstate.faction_turn
            };
        })} />;
        return (
            <div style={{display:"flex", flexDirection:"column"}}>
                <h4>Movement Round</h4>
                {turnOrder}
            </div>
        );
    }
}

module.exports = Movement;