import React from 'react';

import LeaderToken from '../components/leader-token';
import Card from '../components/card';
import Units from './units';


export function PlanLeader({factionState, selectedLeader, active, setLeader}) {
    const handleLeader = (name, power) => {
        let onClick = undefined;
        if (active) {
            onClick = ()=> {
                setLeader(name);
            };
        };
        return {
            onClick: onClick,
            isSelected: selectedLeader === name,
        };
    }
    let meLeaders = factionState.leaders.map((leader) => {
        const [name, power] = leader;
        const {onClick, isSelected} = handleLeader(name, power);
        return <LeaderToken
                    key={name}
                    name={name}
                    selected={isSelected}
                    dead={false} onClick={onClick}/>;
    });
    if (factionState.treachery.indexOf("Cheap-Hero/Heroine") !== -1) {
        const {onClick, isSelected} = handleLeader("Cheap-Here/Heroine", 0);
        meLeaders.push(
            <Card key="Cheap-Hero/Heroine"
                type="Treachery" name="Cheap-Hero/Heroine"
                width={isSelected ? 100 : 75}
                selected={isSelected}
                onClick={onClick} />);
    }
    return (
        <div style={{display:"flex"}}>
            {meLeaders}
        </div>
    );
};

export function PlanNumber({maxUnits, units, setUnits, active}) {
    let unitSetArgs = undefined;
    if (active) {
        unitSetArgs = (units)=>{
            const unitCount = units === "" ? 0 : units.split(",").length;
            setUnits(unitCount);
        };
    }
    const unitCount = units ? parseInt(units) : 0;
    return (
        <div style={{margin: 10}}>
            <Units
                maxOnes={maxUnits}
                args={Array(unitCount).fill("1").join(",")}
                setArgs={unitSetArgs} />
        </div>
    );
}

export function PlanTreachery({title, cards, active, selectedCard, setSelectedCard}) {
    return (
        <div>
            {title}:
            <div style={{display:"flex"}}>
                {cards.map((card)=> {
                    let onClick = undefined;
                    const selected = card === selectedCard;
                    if (active) {
                        onClick = () => {
                            setSelectedCard(selected ? "-" : card);
                        }
                    }
                    return <Card key={card} type="Treachery" name={card} width={selected ? 100 : 75} onClick={onClick} selected={selected} />;
                })}
            </div>
        </div>
    );
};


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
    meFactionState.leaders.forEach((leader) => {
        if (leader[0] === selected.leader) {
            selectedLeaderPower = leader[1];
        }
    });

    const meWeapons = meFactionState.treachery.filter(
        (t)=>state.treachery_reference.weapons.indexOf(t) !== -1);
    const meDefenses = meFactionState.treachery.filter(
        (t)=>state.treachery_reference.defenses.indexOf(t) !== -1);
    const meWorthless = meFactionState.treachery.filter(
        (t)=>state.treachery_reference.worthless.indexOf(t) !== -1);


    const weapons = <PlanTreachery title="Weapon" cards={meWeapons} active={mePlan.weapon === undefined} selectedCard={selected.weapon} setSelectedCard={(selectedCard)=>{
        const newArgs = [selected.leader, selected.units, selectedCard, selected.defense ? selected.defense : "-"].join(" ");
        setArgs(newArgs);
    }} />;

    const defenses = <PlanTreachery title="Defenses" cards={meDefenses} active={mePlan.defense === undefined} selectedCard={selected.defense} setSelectedCard={(selectedCard)=>{
        const newArgs = [selected.leader, selected.units, selected.weapon ? selected.weapon : "-", selectedCard].join(" ");
        setArgs(newArgs);
    }} />;

    return (
        <div className="battle-plan">
            <PlanLeader factionState={meFactionState} selectedLeader={selected.leader} active={mePlan.leader === undefined} setLeader={(leader)=>{
                const newArgs = [leader, selected.units, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-"].join(" ");
                setArgs(newArgs); 
            }} />
            <PlanNumber units={selected.units} active={mePlan.units === undefined} maxUnits={meMaxUnits} setUnits={(units)=>{
                const newArgs = [selected.leader, units, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-"].join(" ");
                setArgs(newArgs);
            }}/>
            Total Power: {selectedLeaderPower + parseInt(selectedUnits)}
            <div style={{display:"flex", justifyContent:"space-around"}}>
                {weapons}
                {defenses}
            </div>
        </div>
    );
}