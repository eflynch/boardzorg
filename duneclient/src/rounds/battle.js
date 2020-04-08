import React from 'react';
import update from 'immutability-helper';

import FactionOrder from '../components/faction-order';
import LeaderToken from '../components/leader-token';
import Card from '../components/card';

const Logo = ({faction, diameter, ...props}) => {
    return <img {...props} src={`/static/app/png/${faction}_logo.png`} width={diameter} height={diameter}/>;
};

const Plan = ({faction, isAttacker, leader, number, weapon, defense, dead}) => {
    const leaderToken = leader !== undefined ? <LeaderToken name={leader[0]}/> : <div>?</div>;
    const numberText = number !== undefined ? number : <span>?</span>;
    const resultText = (number !== undefined && leader !== undefined) ? <span>{number + (dead ? 0 : leader[1])}</span> : <span>?</span>;
    const weaponShow = weapon !== undefined ? <Card type="Treachery" name={weapon ? weapon : "Reverse"} width={100} /> : <span>?</span>;
    const defenseShow = defense !== undefined ? <Card type="Treachery" name={defense ? defense : "Reverse"} width={100} /> : <span>?</span>;
    return (
        <div style={{display:"flex"}}>
            <Logo faction={faction} diameter={20}/>
            <div style={{display:"flex", alignItems: "center"}}>
                {leaderToken}<div className="big-unit"> + {numberText} = {resultText}</div>
            </div>
            {weaponShow}
            {defenseShow}
        </div>
    );
}

export default function Battle({roundstate, factionOrder, interaction, setInteraction}) {
    const battlesToPick = () => {
        const pickable = roundstate.battles.filter((battle)=>{
            return battle[0] == roundstate.faction_turn;
        });

        let active = false;
        if (roundstate.stage === "main" && interaction.mode === "battle-select"){
            active = true;
        }


        const pickers = pickable.map((battle)=> {
            let selected = false;
            if (interaction["battle-select"] === battle.slice(1).join(" ")){
                selected = true;
            }
            if (roundstate.stage === "battle") {
                const activeBattle = roundstate.stage_state.battle;
                if (activeBattle.join(" ") === battle.join(" ")) {
                    selected = true;
                }
            }
            return (
                <div className={"picker" + (active ? " active" : "") + (selected ? " selected": "")} 
                     key={battle.join("-")} onClick={()=>{
                    if (interaction.mode === "battle-select") {
                        setInteraction(update(interaction, {
                            [interaction.mode]: {$set: battle.slice(1).join(" ")},
                            mode: {$set: null},
                        }));
                    }
                }}>
                    <Logo faction={battle[1]} diameter={80}/>
                    <div style={{display:"flex", flexDirection: "column", alignItems:"center", marginLeft:5}}>
                        <div>{battle[2]}</div>
                        <div>{battle[3]}</div>
                    </div>
                </div>
            );
        });

        return (
            <div style={{display:"flex", flexWrap:"wrap"}}>
                {pickers}
            </div>
        );
    };

    const plansRevealed = () => {
        const revealSubStages = ["resolve", "traitors"];
        if (roundstate.stage_state !== undefined && roundstate.stage_state.battle !== undefined) {
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
    }

    const attackerOrder = () => {
        const allFactionsInBattle = {};
        roundstate.battles.forEach((battle)=>{
            allFactionsInBattle[battle[0]] = true;
        });
        const relevantFactionOrder = factionOrder.filter((faction)=>{
            return allFactionsInBattle[faction] !== undefined;
        });
        const turnIndex = relevantFactionOrder.indexOf(roundstate.faction_turn);
        return <FactionOrder factions={relevantFactionOrder.map((faction, i)=>{
            return {
                faction: faction,
                label: turnIndex > i ? "done" : "",
                active: faction === roundstate.faction_turn
            };
        })} />;
    };

    return (
        <div style={{display:"flex", flexDirection:"column", justifyContent:"space-between", alignItems:"stretch"}}>
            <div style={{display:"flex", justifyContent: "space-around", alignItems:"center"}}>
                {attackerOrder()} <span style={{fontSize:30, fontWeight:"bold"}}>vs</span> {battlesToPick()}
            </div>
            {plansRevealed()}
            {/*JSON.stringify(roundstate).replace(",", ", ").replace(":", ": ")*/}
        </div>
    );
};
