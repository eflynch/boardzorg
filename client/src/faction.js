import React, { useState } from 'react';

import TokenPile from './components/token-pile';
import Spice from './components/spice';
import Card from './components/card';
import LeaderToken from './components/leader-token';
import update from 'immutability-helper';


export default function Faction({factionstate, faction, me}) {

    const [show, setShow] = useState(faction === me);

    if (!show) {
        return (
            <div className={"panel menu faction" + (me === faction ? " me" : "")}>
                <b className="menu-toggle" onClick={(e)=>{setShow(true);}} >{faction}</b>
            </div>
        );
    }

    const getTreachery = () => {
        if (!factionstate.hasOwnProperty("treachery")){
            return [];
        }

        if (Array.isArray(factionstate.treachery)){
            return factionstate.treachery.map((name, i) => {
                return <Card type="Treachery" key={i} name={name}/>;
            });
        } else {
            let treachery = [];
            for (let i=0; i < factionstate.treachery.length; i++){
                treachery.push(<Card type="Treachery" key={"reverse-"+i} name="Reverse" />);
            }
            return treachery;
        }
    };

    const getLeaders = () => {
        const allLeaders = factionstate.leaders.concat(factionstate.tank_leaders);
        if (faction == "atreides" &&
            factionstate.kwisatz_haderach_available) {
            allLeaders.push(["Kwisatz-Haderach", 2]);
        }
        return (
            <div style={{display:"flex", flexWrap:"wrap"}}>
                {allLeaders.map((leader) => {
                    let dead = false;
                    if (factionstate.tank_leaders.indexOf(leader) !== -1){
                        dead = true;
                    }
                    if (leader[0] == "Kwisatz-Haderach" && factionstate.kwisatz_haderach_tanks != null) {
                        dead = true;
                    }
                    const leaderName = leader[0];
                    return <LeaderToken
                            key={"leader-"+leaderName}
                            name={leaderName}
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
        let number = factionstate.reserve_units.length;
        let power = factionstate.reserve_units.reduce((a, b) => a + b, 0);
        return <TokenPile width={50} faction={faction} number={number} bonus={power-number}/>
    };

    const getSpice = () => {
        if (factionstate.spice){
            return (
                <div style={{display: "flex", flexDirection: "column", alignItems:"center"}}>
                    Available<Spice width={75} amount={factionstate.spice}/>
                </div>
            );
        }
        return <div/>;
    };

    const getBribeSpice = () => {
        if (factionstate.bribe_spice){
            return (
                <div style={{display: "flex", flexDirection: "column", alignItems:"center"}}>
                    Incoming<Spice width={75} amount={factionstate.bribe_spice}/>
                </div>
            );
        }
        return <div/>;
    };

    return (
        <div className={"panel menu faction" + (me === faction ? " me" : "")}>
            <b className="menu-toggle" onClick={(e)=>{setShow(false);}}>{faction}</b>
            <div className="faction-content">
                {getLeaders()}
                {getTokens()}
                {getSpice()}
                {getBribeSpice()}
                <div style={{display:"flex", flexWrap: "wrap"}}>
                    {getTreachery()}
                    {getTraitors()}
                </div>
            </div>
        </div>
    );
}
