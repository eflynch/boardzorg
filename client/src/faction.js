import React, { useState } from 'react';

import TokenPile from './components/token-pile';
import Hunny from './components/hunny';
import Card from './components/card';
import CharacterToken from './components/character-token';
import update from 'immutability-helper';


export default function Faction({factionstate, faction, me}) {

    const [show, setShow] = useState(false);

    if (!show) {
        return (
            <div className={"faction" + (me === faction ? " me" : "")}>
                <h2 onClick={(e)=>{setShow(true);}} >{faction}</h2>
            </div>
        );
    }

    const getProvisions = () => {
        if (!factionstate.hasOwnProperty("provisions")){
            return [];
        }

        if (Array.isArray(factionstate.provisions)){
            return factionstate.provisions.map((name, i) => {
                return <Card type="Provisions" key={i} name={name}/>;
            });
        } else {
            let provisions = [];
            for (let i=0; i < factionstate.provisions.length; i++){
                provisions.push(<Card type="Provisions" key={"reverse-"+i} name="Reverse" />);
            }
            return provisions;
        }
    };

    const getCharacters = () => {
        const allCharacters = factionstate.characters.concat(factionstate.lost_characters);
        if (faction == "owl" &&
            factionstate.winnie_the_pooh_available) {
            allCharacters.push(["Winnie-The-Pooh", 2]);
        }
        return (
            <div style={{display:"flex", flexWrap:"wrap"}}>
                {allCharacters.map((character) => {
                    let dead = false;
                    if (factionstate.lost_characters.indexOf(character) !== -1){
                        dead = true;
                    }
                    if (character[0] == "Winnie-The-Pooh" && factionstate.winnie_the_pooh_losts != null) {
                        dead = true;
                    }
                    const characterName = character[0];
                    return <CharacterToken
                            key={"character-"+characterName}
                            name={characterName}
                            dead={dead}/>;
                })}
            </div>
        );
    };

    const getTraitors = () => {
        if (me !== faction){
            return [];
        }
        return factionstate.traitors.map((traitor) => {
            const traitorName = traitor[0];
            return <Card type="Traitor"
                    key={"traitor-"+traitorName}
                    name={traitor[0]}/>;
        });
    };

    const getTokens = () => {
        let number = factionstate.reserve_minions.length;
        let power = factionstate.reserve_minions.reduce((a, b) => a + b, 0);
        return <TokenPile width={50} faction={faction} number={number} bonus={power-number}/>
    };

    const getHunny = () => {
        if (factionstate.hunny !== undefined){
            return (
                <div style={{display: "flex", flexDirection: "column", alignItems:"center"}}>
                    Hunny<Hunny width={75} amount={factionstate.hunny}/>
                </div>
            );
        }
        return <div/>;
    };

    const getBribeHunny = () => {
        if (factionstate.bribe_hunny !== undefined){
            return (
                <div style={{display: "flex", flexDirection: "column", alignItems:"center"}}>
                    Bribe<Hunny width={75} amount={factionstate.bribe_hunny}/>
                </div>
            );
        }
        return <div/>;
    };

    return (
        <div className={"faction" + (me === faction ? " me" : "")}>
            <div className="faction-content">
                {getCharacters()}
                {getTokens()}
                {getHunny()}
                <div style={{display:"flex", flexWrap: "wrap"}}>
                    {getProvisions()}
                    {getTraitors()}
                </div>
                {getBribeHunny()}
            </div>
            <h2 onClick={(e)=>{setShow(false);}}>{faction}</h2>
        </div>
    );
}
