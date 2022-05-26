import React from 'react';
import update from 'immutability-helper';

import FactionOrder from '../components/faction-order';
import LeaderToken from '../components/leader-token';
import Card from '../components/card';

const Logo = ({faction, diameter, ...props}) => {
    return <img {...props} src={`/static/app/png/${faction}_logo.png`} width={diameter} height={diameter}/>;
};

const Plan = ({faction, traitor, isAttacker, leader, number, weapon, defense, dead, kwisatz_haderach}) => {
    let leaderToken;
    let leaderValue = 0;
    if (leader !== undefined) {
        if (leader !== null) {
            if (leader[0] === "Cheap-Hero/Heroine") {
                leaderToken = <Card key="Cheap-Hero/Heroine"
                        type="Treachery"
                        name="Cheap-Hero/Heroine"
                        width={cardWidth}/>;
            } else {
                leaderToken = <LeaderToken traitor={traitor} name={leader[0]}/>;
                leaderValue = leader[1];
            }
        } else {
            leaderToken = <span className="question-leader">X</span>;
        }
    } else {
        leaderToken = <span className="question-leader">?</span>;
    }
    const cardWidth = 100;
    const numberText = number !== undefined ? <span>{number}</span> : <span>?</span>;
    const resultText = (number !== undefined && leader !== undefined) ? <span>{number + (dead ? 0 : leaderValue + (kwisatz_haderach ? 2 : 0))}</span> : <span>?</span>;
    const weaponShow = weapon !== undefined ? <Card type="Treachery" name={weapon ? weapon : "Reverse"} width={cardWidth} /> : <span className="question-card">?</span>;
    const defenseShow = defense !== undefined ? <Card type="Treachery" name={defense ? defense : "Reverse"} width={cardWidth} /> : <span className="question-card">?</span>;
    return (
        <div style={{display:"flex", flexDirection:"column", alignItems: "center", fontSize:30}}>
            <div style={{display:"flex", alignItems: "center"}}>
                <div style={{display:"flex", flexDirection:"column", alignItems:"center", marginRight:10}}>
                    {leaderToken}
                    {kwisatz_haderach ? <LeaderToken name="Kwisatz-Haderach"/> : null}
                </div>
                <div className="big-unit"> + {numberText} = {resultText}</div>
            </div>
            <div style={{display:"flex", marginTop:10}}>{weaponShow}{defenseShow}</div>
        </div>
    );
}

export default function Battle({roundstate, factionOrder, interaction, selection}) {
    const antagonists = () => {
        const pickable = roundstate.battles.filter((battle)=>{
            return battle[0] == roundstate.faction_turn;
        });

        let active = false;
        if (roundstate.stage === "main" && interaction.mode === "battle-select"){
            active = true;
        }

        if (roundstate.stage === "battle") {
            return <Logo diameter={80} faction={roundstate.stage_state.battle[1]} />
        }


        const pickers = pickable.map((battle)=> {
            let selected = false;
            if (selection["battle-select"] === battle.slice(1).join(" ")){
                selected = true;
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
                        <div style={{fontSize:10}}>(sector: {battle[3]})</div>
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
                    <div style={{display:"flex", justifyContent:"space-evenly", margin:10}}>
                        <Plan faction={attacker} traitor={traitor_revealers.indexOf(defender) !== -1} isAttacker={true} {...roundstate.stage_state.attacker_plan}/>
                        <div style={{backgroundColor:"white", flexShrink:0, width:1, margin:15}} />
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

    const protagonistOrder = () => {
        const allFactionsInBattle = {};
        roundstate.battles.forEach((battle)=>{
            allFactionsInBattle[battle[0]] = true;
        });
        const relevantFactionOrder = factionOrder.filter((faction)=>{
            return allFactionsInBattle[faction] !== undefined;
        });
        const turnIndex = relevantFactionOrder.indexOf(roundstate.faction_turn);
        return <FactionOrder style={{display:"inline-block"}}diameter={30} factions={relevantFactionOrder.map((faction, i)=>{
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

        let voiceText = "";
        if (stage_state.voice) {
            const [no, proj_pois, weap_def] = stage_state.voice;
            voiceText = [no ? "do not use a" : "use a", proj_pois, weap_def].join(" ")
        }
        
        return (
            <div style={{display:"flex", flexWrap:"wrap", alignItems:"center", justifyContent:"center"}}>
                {stage_state.voice ? <LogoMarker faction="bene-gesserit" name={voiceText}/> : ""}
                {stage_state.karama_sardaukar ? <LogoMarker faction="emperor" name={"No Sardaukar"}/> : ""}
                {stage_state.karama_fedakin ? <LogoMarker faction="fremen" name={"No Fedaykin"}/> : ""}
                {stage_state.karama_kwisatz_haderach ? <LogoMarker faction="atreides" name={"No Kwisatz Haderach"}/> : ""}
            </div>
        );
    };

    return (
        <div style={{display:"flex", flexDirection:"column", justifyContent:"space-between", alignItems:"stretch"}}>
            <div style={{display:"flex", alignItems:"center"}}>
                <span style={{marginRight:10}}>Battling Order: </span>
                {protagonistOrder()}
            </div>
            <div style={{display:"flex", justifyContent: "space-around", alignItems:"center"}}>
                {<Logo diameter={80} faction={roundstate.faction_turn} />} <span style={{fontSize:30, fontWeight:"bold"}}>vs</span> {antagonists()}
            </div>
            <div style={{}}>
                {roundstate.stage === "battle" ? `in ${roundstate.stage_state.battle[2]} (sector ${roundstate.stage_state.battle[3]})` : ""}
            </div>
            {factors()}
            {plansRevealed()}
            {winner()}
        </div>
    );
};
