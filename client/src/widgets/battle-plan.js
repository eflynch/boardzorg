import React from 'react';

import CharacterToken from '../components/character-token';
import Card from '../components/card';
import Minions from './minions';


export function PlanCharacter({characters, provisions, selectedCharacter, active, setCharacter, canDeselect}) {
    const handleCharacter = (name, power) => {
        let onClick = undefined;
        const isSelected = selectedCharacter === name;
        if (active) {
            onClick = ()=> {
                if (isSelected && canDeselect) {
                    setCharacter("-");
                } else {
                    setCharacter(name);
                }
            };
        };
        return {
            onClick: onClick,
            isSelected: isSelected
        };
    };
    let meCharacters = characters.map((character) => {
        const [name, power] = character;
        const {onClick, isSelected} = handleCharacter(name, power);
        return <CharacterToken
                    key={name}
                    name={name}
                    selected={isSelected}
                    dead={false} onClick={onClick}/>;
    });
    if (provisions.indexOf("Stuffed-Animal") !== -1) {
        const {onClick, isSelected} = handleCharacter("Stuffed-Animal", 0);
        meCharacters.push(
            <Card key="Stuffed-Animal"
                type="Provisions" name="Stuffed-Animal"
                width={isSelected ? 100 : 75}
                selected={isSelected}
                onClick={onClick} />);
    }
    return (
        <div style={{display:"flex", alignItems:"center"}}>
            {meCharacters}
        </div>
    );
};

export function PlanNumber({maxNumber, number, setNumber, active}) {
    let minionSetArgs = undefined;
    if (active) {
        minionSetArgs = (minions)=>{
            const minionCount = minions === "" ? 0 : minions.split(",").length;
            setNumber(minionCount);
        };
    }
    const numberParsed = number ? parseInt(number) : 0;
    return (
        <div style={{margin: 10}}>
            <Minions
                maxOnes={maxNumber}
                args={Array(numberParsed).fill("1").join(",")}
                setArgs={minionSetArgs} />
        </div>
    );
}

export function PlanProvisions({title, cards, active, selectedCard, setSelectedCard}) {
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
                    return <Card key={card} type="Provisions" name={card} width={selected ? 100 : 75} onClick={onClick} selected={selected} />;
                })}
            </div>
        </div>
    );
};

function PlanKwisatz({selected, active, setKwisatz}) {
    return <CharacterToken selected={selected} name="Winnie-The-Pooh" onClick={active ? () => {
        setKwisatz(selected ? "-" : "Winnie-The-Pooh");
    } : null}/>;
}

export default function BattlePlan({me, state, args, setArgs, maxPower}) {

    const stageState = state.round_state.stage_state;
    const meFactionState = state.faction_state[me];
    const [attacker, defender, space, sector] = stageState.battle;
    const meMaxNumber = maxPower;
    const iAmAttacker = me === attacker;

    const mePlan = iAmAttacker ? stageState.attacker_plan : stageState.defender_plan;

    const [selectedCharacter, selectedNumber, selectedWeapon, selectedDefense, selectedKwisatz] = args.split(" ");

    const selected = {
        character: mePlan.character === undefined ? (selectedCharacter === "-" ? null : selectedCharacter) : mePlan.character[0],
        number: mePlan.number === undefined ? selectedNumber : mePlan.number,
        weapon: mePlan.weapon === undefined ? (selectedWeapon === "-" ? null : selectedWeapon) : mePlan.weapon,
        defense: mePlan.defense === undefined ? (selectedDefense === "-" ? null : selectedDefense) : mePlan.defense,
        kwisatz: mePlan["winnie-the-pooh"] === undefined ? selectedKwisatz : mePlan["winnie-the-pooh"],
    };

    let selectedCharacterPower = 0;
    meFactionState.characters.forEach((character) => {
        if (character[0] === selected.character) {
            selectedCharacterPower = character[1];
        }
    });

    if (selected.kwisatz === "Winnie-The-Pooh") {
        selectedCharacterPower += 2;
    }

    const meWeapons = meFactionState.provisions.filter(
        (t)=>state.provisions_reference.weapons.indexOf(t) !== -1);

    const meDefenses = meFactionState.provisions.filter(
        (t)=>state.provisions_reference.defenses.indexOf(t) !== -1);

    const meWeaponWorthless = meFactionState.provisions.filter(
        (t)=> {
            return (state.provisions_reference.worthless.indexOf(t) !== -1) && (selected.defense !== t);
        });

    const meDefenseWorthless = meFactionState.provisions.filter(
        (t)=> {
            return (state.provisions_reference.worthless.indexOf(t) !== -1) && (selected.weapon !== t);
        });

    const weapons = <PlanProvisions title="Weapon" cards={meWeapons.concat(meWeaponWorthless)} active={mePlan.weapon === undefined} selectedCard={selected.weapon} setSelectedCard={(selectedCard)=>{
        const newArgs = [selected.character ? selected.character : "-", selected.number, selectedCard, selected.defense ? selected.defense : "-", selected.kwisatz].join(" ");
        setArgs(newArgs);
    }} />;

    const defenses = <PlanProvisions title="Defenses" cards={meDefenses.concat(meDefenseWorthless)} active={mePlan.defense === undefined} selectedCard={selected.defense} setSelectedCard={(selectedCard)=>{
        const newArgs = [selected.character ? selected.character : "-", selected.number, selected.weapon ? selected.weapon : "-", selectedCard, selected.kwisatz].join(" ");
        setArgs(newArgs);
    }} />;

    const kwisatzAvailable =
          (me == "owl") &&
          meFactionState["winnie_the_pooh_available"] &&
          (meFactionState["winnie_the_pooh_losts"] == null) &&
          selected.character &&
          !stageState.author_winnie_the_pooh &&
          ((state.round_state.winnie_the_pooh_character == null) ||
           ((state.round_state.winnie_the_pooh_character === selected.character) &&
            (selected.character != "Stuffed-Animal")));

    const kwisatz = kwisatzAvailable ?
            <PlanKwisatz
             active={mePlan["winnie-the-pooh"] === undefined}
             selected={selected.kwisatz === "Winnie-The-Pooh"}
             setKwisatz={(kwisatz) => {
                 const newArgs = [selected.character ? selected.character : "-", selected.number, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-", kwisatz].join(" ");
                 setArgs(newArgs);
             }}/>
          : null;
    return (
        <div className="battle-plan">
            <PlanCharacter characters={meFactionState.characters} provisions={meFactionState.provisions} selectedCharacter={selected.character} active={mePlan.character === undefined} setCharacter={(character)=>{
                const newArgs = [character, selected.number, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-", "-"].join(" ");
                setArgs(newArgs);
            }} />
            {kwisatz}
            <PlanNumber number={selected.number} active={mePlan.number === undefined} maxNumber={meMaxNumber} setNumber={(number)=>{
                const newArgs = [selected.character ? selected.character : "-", number, selected.weapon ? selected.weapon : "-", selected.defense ? selected.defense : "-", selectedKwisatz].join(" ");
                setArgs(newArgs);
            }}/>
            Total Power: {selectedCharacterPower + parseInt(selectedNumber)}
            <div style={{display:"flex", justifyContent:"space-around"}}>
                {weapons}
                {defenses}
            </div>
        </div>
    );
}
