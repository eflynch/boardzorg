import React from 'react';
import update from 'immutability-helper';

import FactionOrder from '../components/faction-order';
import LeaderToken from '../components/leader-token';
import Card from '../components/card';

const Logo = ({faction, diameter, ...props}) => {
    return <img {...props} src={`/static/app/png/${faction}_logo.png`} width={diameter} height={diameter}/>;
};

const Plan = ({faction, isAttacker, leader, number, weapon, defense, dead}) => {
    return (
        <div style={{display:"flex"}}>
            <Logo faction={faction} diameter={20}/>
            <div style={{display:"flex", alignItems: "center"}}>
                <LeaderToken name={leader[0]}/><div className="big-unit"> + {number} = {number + (dead ? 0 : leader[1])}</div> 
            </div>
            <Card type="Treachery" name={weapon ? weapon : "Reverse"} width={100} />
            <Card type="Treachery" name={defense ? defense : "Reverse"} width={100} />
        </div>
    );
}

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
    if (roundstate.stage_state.substage === "resolve" || roundstate.stage_state.substage === "traitors") {
        const battle = roundstate.stage_state.battle;
        return (
            <div>
                Plans Revealed:
                <div style={{display:"flex"}}>
                    <Plan faction={battle[0]} isAttacker={true} {...roundstate.stage_state.attacker_plan} />
                    <Plan faction={battle[1]} isAttacker={false} {...roundstate.stage_state.defender_plan} />
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
                {/*JSON.stringify(roundstate).replace(",", ", ").replace(":", ": ")*/}
            </div>
        );
    }
}

module.exports = Battle;