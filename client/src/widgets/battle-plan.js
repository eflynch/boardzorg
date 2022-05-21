import React from 'react';

import LeaderToken from '../components/leader-token';
import Card from '../components/card';
import Units from './units';


export function PlanLeader({leaders, treachery, selectedLeader, active, setLeader, canDeselect}) {
    const handleLeader = (name, power) => {
        let onClick = undefined;
        const isSelected = selectedLeader === name;
        if (active) {
            onClick = ()=> {
                if (isSelected && canDeselect) {
                    setLeader("-");
                } else {
                    setLeader(name);
                }
            };
        };
        return {
            onClick: onClick,
            isSelected: isSelected
        };
    };
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
        const {onClick, isSelected} = handleLeader("Cheap-Hero/Heroine", 0);
        meLeaders.push(
            <Card key="Cheap-Hero/Heroine"
                type="Treachery" name="Cheap-Hero/Heroine"
                width={isSelected ? 100 : 75}
                selected={isSelected}
                onClick={onClick} />);
    }
    return (
        <div style={{display:"flex", alignItems:"center"}}>
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

function PlanKwisatz({selected, active, setKwisatz}) {
    return <LeaderToken selected={selected} name="Kwisatz-Haderach" onClick={active ? () => {
        setKwisatz(selected ? "-" : "Kwisatz-Haderach");
    } : null}/>;
}

export default function BattlePlan({me, state, args, setArgs, maxPower}) {

    const stageState = state.round_state.stage_state;
    const meFactionState = state.faction_state[me];
    const [attacker, defender, space, sector] = stageState.battle;
    const meMaxNumber = maxPower;
    const iAmAttacker = me === attacker;

    const mePlan = iAmAttacker ? stageState.attacker_plan : stageState.defender_plan;

    const [selectedLeader, selectedNumber, selectedWeapon, selectedDefense, selectedKwisatz] = args.split(" ");

    const selected = {
        leader: mePlan.leader === undefined ? (selectedLeader === "-" ? null : selectedLeader) : mePlan.leader[0],
        number: mePlan.number === undefined ? selectedNumber : mePlan.number,
        weapon: mePlan.weapon === undefined ? (selectedWeapon === "-" ? null : selectedWeapon) : mePlan.weapon,
        defense: mePlan.defense === undefined ? (selectedDefense === "-" ? null : selectedDefense) : mePlan.defense,
        kwisatz: mePlan["kwisatz-haderach"] === undefined ? selectedKwisatz : mePlan["kwisatz-haderach"],
    };

    let selectedLeaderPower = 0;
    meFactionState.leaders.forEach((leader) => {
        if (leader[0] === selected.leader) {
            selectedLeaderPower = leader[1];
        }
    });

    if (selected.kwisatz === "Kwisatz-Haderach") {
        selectedLeaderPower += 2;
    }

    const meWeapons = meFactionState.treachery.filter(
        (t)=>state.treachery_reference.weapons.indexOf(t) !== -1);

    const meDefenses = meFactionState.treachery.filter(
        (t)=>state.treachery_reference.defenses.indexOf(t) !== -1);

    const meWeaponWorthless = meFactionState.treachery.filter(
        (t)=> {
            return (state.treachery_reference.worthless.indexOf(t) !== -1) && (selected.defense !== t);
        });

    const meDefenseWorthless = meFactionState.treachery.filter(
        (t)=> {
            return (state.treachery_reference.worthless.indexOf(t) !== -1) && (selected.weapon !== t);
        });

    const weapons = <PlanTreachery title="Weapon" cards={meWeapons.concat(meWeaponWorthless)} active={mePlan.weapon === undefined} selectedCard={selected.weapon} setSelectedCard={(selectedCard)=>{
        const newArgs = [selected.leader ? selected.leader : "-", selected.number, selectedCard, selected.defense ? selected.defense : "-", selected.kwisatz].join(" ");
        setArgs(newArgs);
    }} />;

    const defenses = <PlanTreachery title="Defenses" cards={meDefenses.concat(meDefenseWorthless)} active={mePlan.defense === undefined} selectedCard={selected.defense} setSelectedCard={(selectedCard)=>{
        const newArgs = [selected.leader ? selected.leader : "-", selected.number, selected.weapon ? selected.weapon : "-", selectedCard, selected.kwisatz].join(" ");
        setArgs(newArgs);
    }} />;

    const kwisatzAvailable =
          (me == "atreides") &&
          meFactionState["kwisatz_haderach_available"] &&
          (meFactionState["kwisatz_haderach_tanks"] == null) &&
          selected.leader &&
          !stageState.karama_kwisatz_haderach &&
          ((state.round_state.kwisatz_haderach_leader == null) ||
           ((state.round_state.kwisatz_haderach_leader === selected.leader) &&
            (selected.leader != "Cheap-Hero/Heroine")));

    const kwisatz = kwisatzAvailable ?
            <PlanKwisatz
             active={mePlan["kwisatz-haderach"] === undefined}
             selected={selected.kwisatz === "Kwisatz-Haderach"}
             setKwisatz={(kwisatz) => {
                 const newArgs = [selected.leader ? selected.leader : "-", selected.number, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-", kwisatz].join(" ");
                 setArgs(newArgs);
             }}/>
          : null;
    return (
        <div className="battle-plan">
            <PlanLeader leaders={meFactionState.leaders} treachery={meFactionState.treachery} selectedLeader={selected.leader} active={mePlan.leader === undefined} setLeader={(leader)=>{
                const newArgs = [leader, selected.number, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-", "-"].join(" ");
                setArgs(newArgs);
            }} />
            {kwisatz}
            <PlanNumber number={selected.number} active={mePlan.number === undefined} maxNumber={meMaxNumber} setNumber={(number)=>{
                const newArgs = [selected.leader ? selected.leader : "-", number, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-", selectedKwisatz].join(" ");
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
