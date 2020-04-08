import React from 'react';

import LeaderToken from '../components/leader-token';
import Card from '../components/card';
import Units from './units';

export default function BattlePlan({me, state, args, setArgs}) {
    const stageState = state.round_state.stage_state;
    const meFactionState = state.faction_state[me];
    const [attacker, defender, space, sector] = stageState.battle;
    const meMaxUnits = state.map_state.filter(s=>s.name === space)[0].forces[me][sector].reduce((a,b)=>a+b, 0);
    const iAmAttacker = me === attacker;

    const mePlan = iAmAttacker ? stageState.attacker_plan : stageState.defender_plan;
    const [selectedLeader, selectedUnits, selectedWeapon, selectedDefense] = args.split(" ");

    const selected = {
        leader: mePlan.leader === undefined ? selectedLeader : mePlan.leader[0],
        units: mePlan.units === undefined ? selectedUnits : mePlan.units,
        weapon: mePlan.weapon === undefined ? (selectedWeapon === "-" ? null : selectedWeapon) : mePlan.weapon,
        defense: mePlan.defense === undefined ? (selectedDefense === "-" ? null : selectedDefense) : mePlan.defense 
    };

    let selectedLeaderPower = 0;
    const meLeaders = meFactionState.leaders.map((leader) => {
        const [name, power] = leader;
        if (selected.leader === name) {
            selectedLeaderPower = power;
        }
        let onClick = undefined;
        if (mePlan.leader === undefined) {
            onClick = ()=> {
                const newArgs = [name, selected.units, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-"].join(" ");
                setArgs(newArgs); 
            };
        }
        return <LeaderToken
                    key={name}
                    name={name}
                    selected={selected.leader === name}
                    dead={false} onClick={onClick}/>;
    });

    const units = () => {
        let unitSetArgs = undefined;
        if (mePlan.units === undefined) {
            unitSetArgs = (units)=>{
                const unitCount = units === "" ? 0 : units.split(",").length;
                const newArgs = [selected.leader, unitCount, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-"].join(" ");
                console.log(newArgs);
                setArgs(newArgs);
            };
        }
        return (
            <div style={{margin: 10}}>
                <Units
                    maxOnes={meMaxUnits}
                    args={Array(parseInt(selectedUnits)).fill("1").join(",")}
                    setArgs={unitSetArgs} />
            </div>
        );
    };

    const meWeapons = meFactionState.treachery.filter(
        (t)=>state.treachery_reference.weapons.indexOf(t) !== -1);
    const meDefenses = meFactionState.treachery.filter(
        (t)=>state.treachery_reference.defenses.indexOf(t) !== -1);
    const meWorthless = meFactionState.treachery.filter(
        (t)=>state.treachery_reference.worthless.indexOf(t) !== -1);


    const weapons = () => {
        return (
            <div>
                Weapon:
                <div style={{display:"flex"}}>
                    {meWeapons.map((card)=> {
                        let onClick = undefined;
                        if (mePlan.weapon === undefined) {
                            onClick = () => {
                                const newArgs = [selected.leader, selected.units, selected.weapon === card ? "-" : card, selected.defense ? selected.defense : "-"].join(" ");
                                setArgs(newArgs);
                            }
                        }
                        return <Card key={card} type="Treachery" name={card} width={selected.weapon === card ? 100 : 75} onClick={onClick} selected={selected.weapon === card} />;
                    })}
                </div>
            </div>
        );
    };


    const defenses = () => {
        return (
            <div>
                Defenses:
                <div style={{display:"flex"}}>
                    {meDefenses.map((card)=> {
                        let onClick = undefined;
                        if (mePlan.defense === undefined) {
                            onClick = () => {
                                const newArgs = [selected.leader, selected.units, selected.weapon ? selected.weapon : "-", selected.defense === card ? "-" : card].join(" ");
                                setArgs(newArgs);
                            }
                        }
                        return <Card key={card} type="Treachery" name={card} width={selected.defense === card ? 100 : 75} onClick={onClick} selected={selected.defense === card} />;
                    })}
                </div>
            </div>
        );
    };

    return (
        <div className="battle-plan">
            {meLeaders}
            {units()}
            Total Power: {selectedLeaderPower + parseInt(selectedUnits)}
            <div style={{display:"flex", justifyContent:"space-around"}}>
                {weapons()}
                {defenses()}
            </div>
        </div>
    );
}