import React from 'react';
import update from 'immutability-helper';

import FactionOrder from '../components/faction-order';

const Logo = ({faction, diameter, ...props}) => {
    return <img {...props} src={`/static/app/png/${faction}_logo.png`} width={diameter} height={diameter}/>;
};

const StageState = ({roundstate, interaction, setInteraction}) => {
    if (roundstate.stage === "main") {
        const pickable = roundstate.battles.filter((battle)=>{
            return battle[0] == roundstate.faction_turn;
        });

        const pickers = pickable.map((battle)=> {
            return (
                <div className={"picker" + (interaction.mode === "battle-select" ? " active" : "")} 
                     key={battle.join("-")} onClick={()=>{
                    if (interaction.mode === "battle-select") {
                        setInteraction(update(interaction, {
                            [interaction.mode]: {$set: battle.slice(1).join(" ")},
                            mode: {$set: null},
                        }));
                    }
                }}>
                    <Logo faction={battle[1]} diameter={80}/> {battle[2]} {battle[3]}
                </div>
            );
        });

        return (
            <div>
                Battles To Pick From:
                <div style={{display:"flex", flexWrap:"wrap"}}>
                    {pickers}
                </div>
            </div>
        );
    }
    return <div/>;
};


class Battle extends React.Component {
    render () {
        let {roundstate, factionOrder, interaction, setInteraction} = this.props;
        const allFactionsInBattle = {};
        roundstate.battles.forEach((battle)=>{
            allFactionsInBattle[battle[0]] = true;
        });
        const relevantFactionOrder = factionOrder.filter((faction)=>{
            return allFactionsInBattle[faction] !== undefined;
        });
        const turnIndex = relevantFactionOrder.indexOf(roundstate.faction_turn);
        let turnOrder = <FactionOrder factions={relevantFactionOrder.map((faction, i)=>{
            return {
                faction: faction,
                label: turnIndex > i ? "done" : "",
                active: faction === roundstate.faction_turn
            };
        })} />;

        return (
            <div style={{display:"flex", flexDirection:"column"}}>
                <h4>Battle Round</h4>
                Battle Picker: {turnOrder}
                <StageState roundstate={roundstate} interaction={interaction} setInteraction={setInteraction} />
                {JSON.stringify(roundstate)}
            </div>
        );
    }
}

module.exports = Battle;