import React, {useState} from 'react';
import Slider, { Range } from 'rc-slider';
import update from 'immutability-helper';

import BattlePlan, {PlanCharacter, PlanNumber, PlanProvisions} from './widgets/battle-plan';
import TraitorSelect from './widgets/traitor-select';
import Integer from './widgets/integer';
import Minions from './widgets/minions';
import Card from './components/card';
import Logo from './components/logo';


const humanReadable = {
    "token-select": "Token Placement",
    "space-sector-select-start": "From",
    "space-sector-select-end": "To",
    "traitor-select": "Traitor",
    "character-input": "Character",
    "space-select": "Space",
};

const Options = ({args, setArgs, options}) => {
    return (
        <div style={{display:"flex", justifyContent:"space-evenly", flexWrap: "wrap", maxWidth:400}}>
            {options.map((option)=> {
                return <div key={option} className={"option" + (option === args ? " selected": "")} onClick={()=>{
                    setArgs(option);
                }}>{option}</div>;
            })}
        </div>
    );
};


const FlightAnswer = ({me, state, args, setArgs, maxPower}) => {
    const stageState = state.round_state.stage_state;
    const query = stageState.flight;
    if (query === "character") {
        const fs = state.faction_state[me];
        return <PlanCharacter characters={fs.characters} provisions={fs.provisions} selectedCharacter={args} setCharacter={setArgs} active={true} />;
    } else if (query === "number") {
        const [space, sector] = stageState.battle.slice(2);
        return <PlanNumber maxNumber={maxPower} number={parseInt(args)} setNumber={(number)=>{
            setArgs("" +number);
        }} active={true} />;
    } else if (query === "weapon") {
        const meWeapons = state.faction_state[me].provisions.filter(
            (t)=>state.provisions_reference.weapons.indexOf(t) !== -1);
        return <PlanProvisions title="Weapon" cards={meWeapons} selectedCard={args} setSelectedCard={setArgs} active={true} />;
    } else if (query === "defense") {
        const meDefenses = state.faction_state[me].provisions.filter(
            (t)=>state.provisions_reference.defenses.indexOf(t) !== -1);
        return <PlanProvisions title="Defense" cards={meDefenses} selectedCard={args} setSelectedCard={setArgs} active={true} />;
    }
};


const MinionSelect = ({value, selected, active, setSelected}) => {
    return <div style={{
        cursor:"pointer",
        width: 20,
        height: 20,
        border: "1px solid black",
        borderRadius: 10,
        backgroundColor: selected ? "red" : "white",
        opacity: selected || active ? 1 : 0.2,
        color: selected? "white" : "black",
        userSelect: "none",
    }} onClick={()=>{
        if (selected) {setSelected(false);}
        else if (active){setSelected(true);}
    }}>{value}</div>;
}

const MinionPicker = ({available, selected, setSelected, canAddMore}) => {
  const minionSelectors = []
  for (const type of Object.keys(available)) {
    for (const index of Array(available[type]).keys()) {
      const isSelected = selected[type] && index < selected[type];
      minionSelectors.push(<MinionSelect
           key={`${type}-${index}`}
           value={type}
           active={isSelected || canAddMore}
           selected={isSelected}
           setSelected={(s)=>{
             setSelected(update(selected, {[type]: {$set: selected[type] + (s ? 1 : -1)}}));
           }}
          />);
    }
  }
  return <div style={{display:"flex"}}>{minionSelectors}</div>;
};

const LostMinions = ({me, state, args, setArgs}) => {
    const selectedMinions = {};
    let totalSelected = 0;
    if (args !== "") {
        args.split(" ").forEach((a)=>{
            const [sector, minions] = a.split(":");
            const minionsParsed = minions.split(",").map((i)=>parseInt(i));
            const numOnes = minionsParsed.filter((i)=>i===1).length;
            const numTwos = minionsParsed.filter((i)=>i===2).length;
            selectedMinions[sector] = {
                1: numOnes,
                2: numTwos
            };
            totalSelected += numOnes + (2*numTwos);
        });
    }


    const [attacker, defender, space, sector] = state.round_state.stage_state.battle;
    const forces = state.map_state.filter(s=>s.name === space)[0].forces[me];
    const sectors = Object.keys(forces);

    sectors.forEach((sector)=> {
        if (selectedMinions[sector] === undefined) {
            selectedMinions[sector] = {1: 0, 2: 0};
        }
    });


    const toLost = me === attacker ? state.round_state.stage_state.attacker_plan.number : state.round_state.stage_state.defender_plan.number;
    const active = totalSelected < toLost;

    const _formatArgs = (selectedMinions) => {
        const sectors = Object.keys(selectedMinions);
        return sectors.map((s)=>{
            return `${s}:${Array(selectedMinions[s][1]).fill("1").concat(Array(selectedMinions[s][2]).fill("2")).join(",")}`;
        }).join(" ");
    };

    return (
        <div>
            <div style={{textAlign: "left"}}><span>Select {toLost - totalSelected} more power:</span></div>
            {sectors.map((sector)=>{
                const availableForcesFlat = forces[sector].slice().sort();
                const availableForces = {};
                for (const force of availableForcesFlat) {
                  if (!availableForces[force]) {
                    availableForces[force] = 1;
                  } else {
                    availableForces[force] += 1;
                  }
                }
                const selectedForces = selectedMinions[sector];
                return (
                    <div key={"sector" + sector} style={{display:"flex", alignItems:"center", justifyContent:"space-between"}}>
                        <span>Sector {sector}:</span>
                        <MinionPicker selected={selectedForces}
                                    available={availableForces}
                                    canAddMore={active}
                                    setSelected={(newSelected) => {
                                      setArgs(_formatArgs(update(selectedMinions, {[sector]: {$set: newSelected}})));
                                    }}
                        />
                    </div>
                );
            })}
        </div>
    );
};

const DiscardProvisions = ({state, me, args, setArgs}) => {
    let weaponSelected = false;
    let defenseSelected = false;
    if (args !== "") {
        weaponSelected = args.split(" ").indexOf("weapon") !== -1;
        defenseSelected = args.split(" ").indexOf("defense") !== -1;
    }
    const [attacker, defender, space, sector] = state.round_state.stage_state.battle;
    const weapon = me === attacker ? state.round_state.stage_state.attacker_plan.weapon : state.round_state.stage_state.defender_plan.weapon;
    const defense = me === attacker ? state.round_state.stage_state.attacker_plan.defense : state.round_state.stage_state.defender_plan.defense;

    const _option = (maybeCard, selected, kind) => {
        if (maybeCard) {
            return <Card type="Provisions" name={maybeCard} selected={selected} width={100} onClick={()=>{
                if (kind === "weapon"){
                    setArgs([!weaponSelected ? "weapon" : "", defenseSelected ? "defense" : ""].join(" "))
                } else {
                    setArgs([weaponSelected ? "weapon" : "", !defenseSelected ? "defense" : ""].join(" "))
                }
            }}/>;
        }
    }
    return (
        <div style={{display:"flex"}}>
            {_option(weapon, weaponSelected, "weapon")}
            {_option(defense, defenseSelected, "defense")}
        </div>
    );
};


const ReturnProvisions = ({state, me, args, setArgs, number}) => {
    const selectedCards = args ? args.split(" ") : [];
    const numSelected = selectedCards.length;
    const provisions = state.faction_state[me].provisions;

    return (
        <div style={{display:"flex"}}>
            {provisions.map((card, i)=> {
                const selected = selectedCards.indexOf(card) !== -1;
                return <Card key={card + i} type="Provisions" name={card} selected={selected} width={100} onClick={()=>{
                    if (selected) {
                        const index = selectedCards.indexOf(card)
                        selectedCards.splice(index, 1);
                        setArgs(selectedCards.join(" "));
                    } else {
                        if (numSelected < number) {
                            selectedCards.push(card)
                            setArgs(selectedCards.join(" "));
                        }
                    }
                }
                }/>;
            })}
        </div>
    );
};
 
const Choice = ({args, setArgs, clearSelection, config, ...props}) => {
    return (
        <div>
            {config.map((subWidget, i) => {
                return (
                    <div key={i}>
                        <Widget {...props} key={i} type={subWidget.widget} config={subWidget.args} args={args} setArgs={(args) => {
                            clearSelection();
                            setArgs(args);
                        }} clearSelection={clearSelection}/>
                    </div>
                );
            })}
        </div>
    );
};

const Struct = ({args, setArgs, config, ...props}) => {
    return (
        <div>
            {config.map((subWidget, i) => {
                return <Widget {...props} key={i} type={subWidget.widget} config={subWidget.args} setArgs={(subArgs)=> {
                    setArgs((args) => {
                        return update(args, {[i]: {$set: subArgs}});
                    });
                }} args={args[i]} />
            })}
        </div>
    );
};

const ArrayWidget = ({args, setArgs, config, ...props}) => {
    const subArgs = args.split(":");
    let widgets = subArgs.map((arg, i) => {
        return <Widget {...props} key={i} type={config.widget} config={config.args} args={arg} setArgs={(args)=> {
            setArgs(update(subArgs, {[i]: {$set: args}}).join(":"));
        }} args={subArgs[i]} />;
    });

    return (
        <div>
            {widgets}
            <button onClick={(e)=>{setArgs(args + ":")}} >+</button>
        </div>
    );
};

const Input = ({args, setArgs, config}) => {
    return <input value={args} onChange={((e)=>{
        const value = e.target.value;
        setArgs(value);
    })}/>;
};

const Constant = ({value, setArgs}) => {
    return <button onClick={()=>{setArgs(value);}}>{value}</button>;
}


const SelectOnMap = ({args, setArgs, interaction, setInteraction, mode, nullable, updateSelection}) => {
    const setAndSelectArgs = (newArgs) => {
        updateSelection(mode, newArgs);
        setArgs(newArgs);
    };

    let pieces = [
            <div key="select" className={"select-on-map" + (mode === interaction.mode ? " on" : " off")} onClick={(e)=>{
                setAndSelectArgs("");
                setInteraction({
                        mode,
                        action: (val) => {
                            setAndSelectArgs(val);
                        },
                });
            }}>Select on Board</div>,
    ];
    if (args && args !== "-") {
        pieces.push(<div key="value">Selected: {args}</div>);
    }
    if (nullable) {
        pieces.push(<div onClick={(e)=>{
            setArgs("");
        }}>x</div>);
    }
    return (
        <div style={{display:"flex", flexDirection: "column", alignItems:"center"}}>
            <span>{(mode in humanReadable) ? humanReadable[mode] : mode}:</span>
            {pieces}
        </div>
    );
};



const FactionSelector = ({faction, selected, diameter, onSelect}) => {
    return (
        <Logo className={"select-faction" + (selected ? " selected" : "")} onClick={onSelect} faction={faction} diameter={diameter} />
    );
}

const FactionSelect = ({args, setArgs, factionsAvailable, allowMulti}) => {
    const selectedFactions = args ? args.split(" ") : [];
    return (
        <div style={{display:"flex", justifyContent:"space-around", flexWrap:"wrap"}}>
            {factionsAvailable.map((faction)=> {
                const selected = selectedFactions.indexOf(faction) !== -1;
                return <FactionSelector diameter={75} key={faction} faction={faction} selected={selected} onSelect={()=>{
                    if (allowMulti) {
                        if (selected) {
                            setArgs(selectedFactions.filter(f => f !== faction).join(" "));
                        } else {
                            selectedFactions.push(faction);
                            setArgs(selectedFactions.join(" "));
                        }
                    } else {
                        setArgs(selected ? "" : faction);
                    }
                }} />;
            })}
        </div>
    );
};

const ChristopherRobbinPlacementSelect = ({args, setArgs, config}) => {
    const [tabr, west, south, westSector, southSector] = args.split(":");
    return (
        <div>
            <h3>Rabbits House</h3>
            <Minions args={tabr} setArgs={(args)=>{
                setArgs([args, west, south, westSector, southSector].join(":"));
            }} woozles={true} />
            <h3>Where The Woozle Wasnt</h3>
            <Minions args={west} setArgs={(args)=>{
                setArgs([tabr, args, south, westSector, southSector].join(":"));
            }} woozles={true} />
            Sector:
            <Integer min={15} max={17} args={westSector} setArgs={(args)=>{
                setArgs([tabr, west, south, args, southSector].join(":"));
            }}/>
            <h3>Leftern Woods</h3>
            <Minions args={south} setArgs={(args)=>{
                setArgs([tabr, west, args, westSector, southSector].join(":"));
            }} woozles={true} />
            Sector:
            <Integer min={3} max={4} args={southSector} setArgs={(args)=>{
                setArgs([tabr, west, south, westSector, args].join(":"));
            }}/>
        </div>
    );
};

const RetrievalCharacter = ({me, args, characters, setArgs, required}) => {
    return <PlanCharacter characters={characters} provisions={[]} selectedCharacter={args} setCharacter={(character)=>{
        if (character) {
            setArgs(character);
        } else {
            setArgs('-');
        }
    }} active={true} canDeselect={!required}/>;
};

const RetrievalMinions = ({me, args, setArgs, minions, maxMinions, single2, title}) => {
    const minionArgs = title ? (args ? args.split(" ")[1] : "") : args;
    const hasMinionsSelected = (minionArgs.indexOf("1") !== -1) || (minionArgs.indexOf("2") !== -1);
    const minionsSelected = hasMinionsSelected ? minionArgs.split(",").map((u)=>parseInt(u)).filter((u)=>u) : [];
    const selectedMinions = {
      1: minionsSelected.filter((u)=>u==1).length,
      2: minionsSelected.filter((u)=>u==2).length,
    };

    const numTwosAvailable = (() => {
        const numTwosAvailable = Math.min(minions.filter((u)=>u==2).length, maxMinions);
        if (single2 && numTwosAvailable) {
             return 1;
        }
        return numTwosAvailable;
    })();

    const numOnesAvailable = Math.min(minions.filter((u)=>u==1).length, maxMinions);
    const availableMinions = {
      1: numOnesAvailable,
      2: numTwosAvailable,
    };
    const active = minionsSelected.length < maxMinions;

    return <MinionPicker available={availableMinions}
                       selected={selectedMinions}
                       setSelected={(newSelected) => {
                         const newSelectedString = `${Array(newSelected[1]).fill("1").concat(Array(newSelected[2]).fill("2")).join(",")}`;
                         if (title) {
                           setArgs([title, newSelectedString].join(" "));
                         } else {
                           setArgs(newSelectedString);
                         }
                       }}
                       canAddMore={active}/>;
};


const Widget = (props) => {
    const {me, state, type, args, config, interaction, setInteraction, clearSelection, updateSelection, setArgs} = props;

    if (type === "null") {
        return "";
    }

    if (type === "choice") {
        return <Choice state={state} me={me} args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction} updateSelection={updateSelection} clearSelection={clearSelection}/>; 
    }

    if (type === "struct") {
        return <Struct state={state} me={me} args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction} updateSelection={updateSelection} clearSelection={clearSelection}/>; 
    }

    if (type === "input") {
        return <Input args={args} setArgs={setArgs} config={config} updateSelection/>; 
    }

    if (type === "faction-select") {
        const factionsAvailable = Object.keys(state.faction_state).filter(f => f !== me);
        return <FactionSelect allowMulti={false} factionsAvailable={factionsAvailable} args={args} setArgs={setArgs} />;
    }

    if (type === "multi-faction-select") {
        return <FactionSelect allowMulti={true} factionsAvailable={config.factions} args={args} setArgs={setArgs} />;
    }


    if (type === "constant") {
        return <Constant value={config} setArgs={setArgs} />;
    }

    if (type === "minions") {
        return <Minions args={args} setArgs={setArgs} woozles={config.woozles} very_sad_boys={config.very_sad_boys}/>;
    }

    if (type === "token-select") {
        return <SelectOnMap mode="token-select" interaction={interaction} setInteraction={setInteraction} setArgs={setArgs} updateSelection={updateSelection} args={args} />;
    }

    if (type === "array") {
        return <ArrayWidget args={args} setArgs={setArgs} config={config} state={state} me={me} />;
    }

    if (type === "christopher_robbin-placement-select") {
        return <ChristopherRobbinPlacementSelect args={args} setArgs={setArgs} config={config} />;
    }

    if (type === "integer") {
        return <Integer args={args} setArgs={setArgs} type={config.type} min={config.min} max={config.max} />;
    }

    if (type === "space-select") {
        return <SelectOnMap mode="space-select" args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction} updateSelection={updateSelection}/>;
    }

    if (type === "space-sector-select-start") {
        return <SelectOnMap mode="space-sector-select-start" args={args} setArgs={setArgs} config={config} interaction={interaction}  setInteraction={setInteraction} updateSelection={updateSelection}/>;
    }

    if (type === "space-sector-select-end") {
        return <SelectOnMap mode="space-sector-select-end" args={args} setArgs={setArgs} config={config} interaction={interaction}  setInteraction={setInteraction} updateSelection={updateSelection}/>;
    }

    if (type === "traitor-select") {
        return <TraitorSelect selected={args} select={setArgs} factionState={state.faction_state[me]}/>;
    }

    if (type === "battle-select") {
        return <SelectOnMap mode="battle-select" setInteraction={setInteraction} setArgs={setArgs} interaction={interaction}  updateSelection={updateSelection}/>;
    }

    if (type === "battle-plan") {
        return <BattlePlan me={me} state={state} args={args} setArgs={setArgs} maxPower={config.max_power} />;
    }

    if (type === "flight") {
        return <Options options={["character", "number", "weapon", "defense"]} args={args} setArgs={setArgs} />;
    }

    if (type === "flight-answer") {
        return <FlightAnswer state={state} me={me} args={args} setArgs={setArgs} maxPower={config.max_power} />;
    }

    if (type === "lost-minions") {
        return <LostMinions state={state} me={me} args={args} setArgs={setArgs} />;
    }

    if (type === "discard-provisions") {
        return <DiscardProvisions state={state} me={me} args={args} setArgs={setArgs} />;
    }

    if (type === "return-provisions") {
        return <ReturnProvisions state={state} me={me} args={args} setArgs={setArgs} number={config.number} />;
    }

    if (type === "cleverness") {
        return <Options options={[
            "bee_trouble-weapon", "bee_trouble-defense", "projectile-weapon", "projectile-defense",
            "no bee_trouble-weapon", "no bee_trouble-defense", "no projectile-weapon", "no projectile-defense",
            "anti_umbrella", "no anti_umbrella", "worthless", "no worthless", "cheap-hero-heroine", "no cheap-hero-heroine",
        ]} args={args} setArgs={setArgs} />;
    }

    if (type === "retrieval-minions") {
        return <RetrievalMinions args={args} setArgs={setArgs} minions={config.minions} maxMinions={config.maxMinions} single2={config.single2} title={config.title}/>;
    }
    if (type === "retrieval-character") {
        return <RetrievalCharacter args={args} setArgs={setArgs} characters={config.characters} required={config.required}/>;
    }
    console.warn(type);

    return <span>
        <span>{(type in humanReadable) ? humanReadable[type] : type}:</span>
        <Input args={args} setArgs={setArgs} config={config} />
    </span>;
};

module.exports = Widget;

