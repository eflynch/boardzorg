import React from 'react';
import update from 'immutability-helper';

import FactionOrder from '../components/faction-order';
import CharacterToken from '../components/character-token';
import Card from '../components/card';

const Logo = ({faction, diameter, ...props}) => {
    return <img {...props} src={`/static/app/png/${faction}_logo.png`} width={diameter} height={diameter}/>;
};

const Plan = ({faction, traitor, isAttacker, character, number, weapon, defense, dead, winnie_the_pooh}) => {
    let characterToken;
    let characterValue = 0;
    if (character !== undefined) {
        if (character !== null) {
            if (character[0] === "Stuffed-Animal") {
                characterToken = <Card key="Stuffed-Animal"
                        type="Provisions"
                        name="Stuffed-Animal"
                        width={cardWidth}/>;
            } else {
                characterToken = <CharacterToken traitor={traitor} name={character[0]}/>;
                characterValue = character[1];
            }
        } else {
            characterToken = <span className="question-character">X</span>;
        }
    } else {
        characterToken = <span className="question-character">?</span>;
    }
    const cardWidth = 100;
    const numberText = number !== undefined ? number : <span>?</span>;
    const resultText = (number !== undefined && character !== undefined) ? <span>{number + (dead ? 0 : characterValue + (winnie_the_pooh ? 2 : 0))}</span> : <span>?</span>;
    const weaponShow = weapon !== undefined ? <Card type="Provisions" name={weapon ? weapon : "Reverse"} width={cardWidth} /> : <span className="question-card">?</span>;
    const defenseShow = defense !== undefined ? <Card type="Provisions" name={defense ? defense : "Reverse"} width={cardWidth} /> : <span className="question-card">?</span>;
    return (
        <div style={{display:"flex", alignItems: "center"}}>
            <div style={{display:"flex", alignItems: "center"}}>
                <div style={{display:"flex", flexDirection:"column", alignItems:"center"}}>
                    {characterToken}
                    {winnie_the_pooh ? <CharacterToken name="Winnie-The-Pooh"/> : null}
                </div>
                    <div className="big-minion"> + {numberText} = {resultText} : </div>
            </div><div style={{width:5, height:1}}/>{weaponShow} {defenseShow}
        </div>
    );
}

export default function Battle({roundstate, factionOrder, interaction, selection}) {
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
            if (selection["battle-select"] === battle.slice(1).join(" ")){
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
                         interaction.action(battle.slice(1).join(" "));
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
        const revealSubStages = ["resolve", "traitors", "winner"];
        if (roundstate.stage_state !== undefined && roundstate.stage_state.battle !== undefined) {
            const [attacker, defender, space, sector] = roundstate.stage_state.battle;
            const traitor_revealers = roundstate.stage_state.traitor_revealers;
            return (
                <div>
                    Plans Revealed:
                    <div style={{display:"flex", justifyContent:"space-around"}}>
                        <Plan faction={attacker} traitor={traitor_revealers.indexOf(defender) !== -1} isAttacker={true} {...roundstate.stage_state.attacker_plan}/>
                        <Plan faction={defender} traitor={traitor_revealers.indexOf(attacker) !== -1} isAttacker={false} {...roundstate.stage_state.defender_plan}/>
                    </div>
                </div>
            );
        }
    }

    const winner = () => {
        if (roundstate.stage_state !== undefined && roundstate.stage_state.battle !== undefined && roundstate.stage_state.winner) {
            return (
                <div className="winner">
                    {roundstate.stage_state.winner} Wins!
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

    const factors = () => {
        if (roundstate.stage !== "battle") {
            return;
        }
        const stage_state = roundstate.stage_state;

        const LogoMarker = ({faction, name}) => {
            return (
               <div style={{
                    position:"relative", height:80, width:150, backgroundColor:"black",
                    border:"1px white solid", borderRadius:5, marginLeft:5, marginRight:5
                }}>
                    <Logo style={{position:"absolute", top:0, left: 35}} faction={faction} diameter={80}/>
                    <div style={{
                        position:"absolute", top: 20, left: 0, width:150, height: 40, display:"flex",
                        justifyContent:"center", alignItems:"center", backgroundColor:"rgba(0, 0, 0, 0.7)"
                    }}>
                        <span>{name}</span>
                    </div>
                </div>
            );
        }

        let clevernessText = "";
        if (stage_state.cleverness) {
            const [no, proj_pois, weap_def] = stage_state.cleverness;
            clevernessText = [no ? "no" : "yes", proj_pois, weap_def].join(" ")
        }
        
        return (
            <div style={{display:"flex", flexWrap:"wrap", alignItems:"center", justifyContent:"center"}}>
                {stage_state.cleverness ? <LogoMarker faction="rabbit" name={clevernessText}/> : ""}
                {stage_state.author_very_sad_boys ? <LogoMarker faction="eeyore" name={"No VerySadBoys"}/> : ""}
                {stage_state.author_fedakin ? <LogoMarker faction="christopher_robbin" name={"No Woozles"}/> : ""}
                {stage_state.author_winnie_the_pooh ? <LogoMarker faction="owl" name={"No Kwisatz Haderach"}/> : ""}
            </div>
        );
    };

    return (
        <div style={{display:"flex", flexDirection:"column", justifyContent:"space-between", alignItems:"stretch"}}>
            <div style={{display:"flex", justifyContent: "space-around", alignItems:"center"}}>
                {attackerOrder()} <span style={{fontSize:30, fontWeight:"bold"}}>vs</span> {battlesToPick()}
            </div>
            {factors()}
            {plansRevealed()}
            {winner()}
            {/*JSON.stringify(roundstate).replace(",", ", ").replace(":", ": ")*/}
        </div>
    );
};
