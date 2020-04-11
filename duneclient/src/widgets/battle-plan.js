import React from 'react';

import LeaderToken from '../components/leader-token';
import Card from '../components/card';
import Units from './units';


export function PlanLeader({leaders, treachery, selectedLeader, active, setLeader}) {
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
    let meLeaders = leaders.map((leader) => {
        const [name, power] = leader;
        const {onClick, isSelected} = handleLeader(name, power);
        return <LeaderToken
                    key={name}
                    name={name}
                    selected={isSelected}
                    dead={false} onClick={onClick}/>;
    });
    if (treachery.indexOf("Cheap-Hero/Heroine") !== -1) {
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

export function PlanNumber({maxNumber, number, setNumber, active}) {
    let unitSetArgs = undefined;
    if (active) {
        unitSetArgs = (units)=>{
            const unitCount = units === "" ? 0 : units.split(",").length;
            setNumber(unitCount);
        };
    }
    const numberParsed = number ? parseInt(number) : 0;
    return (
        <div style={{margin: 10}}>
            <Units
                maxOnes={maxNumber}
                args={Array(numberParsed).fill("1").join(",")}
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


export default function BattlePlan({me, state, args, setArgs, maxPower}) {

    const stageState = state.round_state.stage_state;
    const meFactionState = state.faction_state[me];
    const [attacker, defender, space, sector] = stageState.battle;
    const meMaxNumber = maxPower;
    const iAmAttacker = me === attacker;

    const mePlan = iAmAttacker ? stageState.attacker_plan : stageState.defender_plan;

    const [selectedLeader, selectedNumber, selectedWeapon, selectedDefense] = args.split(" ");

    const selected = {
        leader: mePlan.leader === undefined ? selectedLeader : mePlan.leader[0],
        number: mePlan.number === undefined ? selectedNumber : mePlan.number,
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
        const newArgs = [selected.leader, selected.number, selectedCard, selected.defense ? selected.defense : "-"].join(" ");
        setArgs(newArgs);
    }} />;

    const defenses = <PlanTreachery title="Defenses" cards={meDefenses} active={mePlan.defense === undefined} selectedCard={selected.defense} setSelectedCard={(selectedCard)=>{
        const newArgs = [selected.leader, selected.number, selected.weapon ? selected.weapon : "-", selectedCard].join(" ");
        setArgs(newArgs);
    }} />;

    return (
        <div className="battle-plan">
            <PlanLeader leaders={meFactionState.leaders} treachery={meFactionState.treachery} selectedLeader={selected.leader} active={mePlan.leader === undefined} setLeader={(leader)=>{
                const newArgs = [leader, selected.number, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-"].join(" ");
                setArgs(newArgs); 
            }} />
            <PlanNumber number={selected.number} active={mePlan.number === undefined} maxNumber={meMaxNumber} setNumber={(number)=>{
                const newArgs = [selected.leader, number, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-"].join(" ");
                setArgs(newArgs);
            }}/>
            Total Power: {selectedLeaderPower + parseInt(selectedNumber)}
            <div style={{display:"flex", justifyContent:"space-around"}}>
                {weapons}
                {defenses}
            </div>
        </div>
    );
}