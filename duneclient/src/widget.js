import React, {useState} from 'react';
import Select from 'react-select';
import Slider, { Range } from 'rc-slider';
import update from 'immutability-helper';

import BattlePlan, {PlanLeader, PlanNumber, PlanTreachery} from './widgets/battle-plan';
import TraitorSelect from './widgets/traitor-select';
import Integer from './widgets/integer';
import Units from './widgets/units';
import Card from './components/card';


const AllFactions = ["emperor", "fremen", "guild", "bene-gesserit", "harkonnen", "atreides"];

const humanReadable = {
    "token-select": "Token Placement",
    "space-sector-select-start": "From",
    "space-sector-select-end": "To",
    "traitor-select": "Traitor",
    "leader-input": "Leader",
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


const PrescienceAnswer = ({me, state, args, setArgs, maxPower}) => {
    const stageState = state.round_state.stage_state;
    const query = stageState.prescience;
    if (query === "leader") {
        const fs = state.faction_state[me];
        return <PlanLeader leaders={fs.leaders} treachery={fs.treachery} selectedLeader={args} setLeader={setArgs} active={true} />;
    } else if (query === "number") {
        const [space, sector] = stageState.battle.slice(2);
        return <PlanNumber maxNumber={maxPower} number={parseInt(args)} setNumber={(number)=>{
            setArgs("" +number);
        }} active={true} />;
    } else if (query === "weapon") {
        const meWeapons = state.faction_state[me].treachery.filter(
            (t)=>state.treachery_reference.weapons.indexOf(t) !== -1);
        return <PlanTreachery title="Weapon" cards={meWeapons} selectedCard={args} setSelectedCard={setArgs} active={true} />;
    } else if (query === "defense") {
        const meDefenses = state.faction_state[me].treachery.filter(
            (t)=>state.treachery_reference.defenses.indexOf(t) !== -1);
        return <PlanTreachery title="Defense" cards={meDefenses} selectedCard={args} setSelectedCard={setArgs} active={true} />;
    }
};


const UnitSelect = ({value, selected, active, setSelected}) => {
    return <div style={{
        cursor:"pointer",
        width: 20,
        height: 20,
        border: "1px solid black",
        borderRadius: 10,
        backgroundColor: selected ? "red" : "white",
        opacity: selected || active ? 1 : 0.2,
        color: selected? "white" : "black"
    }} onClick={()=>{
        if (selected) {setSelected(false);}
        else if (active){setSelected(true);}
    }}>{value}</div>;
}

const TankUnits = ({me, state, args, setArgs}) => {
    const selectedUnits = {};
    let totalSelected = 0;
    if (args !== "") {
        args.split(" ").forEach((a)=>{
            const [sector, units] = a.split(":");
            const unitsParsed = units.split(",").map((i)=>parseInt(i));
            const numOnes = unitsParsed.filter((i)=>i===1).length;
            const numTwos = unitsParsed.filter((i)=>i===2).length;
            selectedUnits[sector] = {
                ones: numOnes,
                twos: numTwos
            };
            totalSelected += numOnes + (2*numTwos);
        });
    }


    const [attacker, defender, space, sector] = state.round_state.stage_state.battle;
    const forces = state.map_state.filter(s=>s.name === space)[0].forces[me];
    const sectors = Object.keys(forces);

    sectors.forEach((sector)=> {
        if (selectedUnits[sector] === undefined) {
            selectedUnits[sector] = {ones: 0, twos: 0};
        }
    });


    const toTank = me === attacker ? state.round_state.stage_state.attacker_plan.number : state.round_state.stage_state.defender_plan.number;
    const active = totalSelected < toTank;

    const _formatArgs = (selectedUnits) => {
        const sectors = Object.keys(selectedUnits);
        return sectors.map((s)=>{
            return `${s}:${Array(selectedUnits[s].ones).fill("1").join(",")}${Array(selectedUnits[s].twos).fill("2").join(",")}`;
        }).join(" ");
    };

    return (
        <div>
            {sectors.map((sector)=>{
                const availableForces = forces[sector].slice().sort();  
                const selectedForces = selectedUnits[sector];
                let oneCount = 0;
                let twoCount = 0;
                return (
                    <div key={"sector" + sector} style={{display:"flex", alignItems:"center", justifyContent:"space-between"}}>
                        <span>Sector {sector}:</span>
                        <div style={{display:"flex", alignItems:"center", flexWrap:"wrap"}}>
                            {availableForces.map((v) => {
                                if (v === 1) {
                                    oneCount += 1;
                                    return <UnitSelect key={"one" + oneCount} value={1} active={active} selected={oneCount <= selectedForces.ones} setSelected={(s)=>{
                                        const newSelectedUnits = update(selectedUnits, {
                                            [sector]: {ones: {$set: selectedForces.ones + (s ? 1 : -1)}}
                                        });
                                        setArgs(_formatArgs(newSelectedUnits));
                                    }}/>
                                }
                                if (v === 2){
                                    twoCount += 1;
                                    return <UnitSelect key={"two" + twoCount} value={2} active={active} selected={twoCount <= selectedForces.twos} setSelected={(s)=>{
                                        const newSelectedUnits = update(selectedUnits, {
                                            [sector]: {twos: {$set: selectedForces.twos + (s ? 2 : -2)}}
                                        });
                                        setArgs(_formatArgs(newSelectedUnits));
                                    }}/>
                                }
                            })}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

const DiscardTreachery = ({state, me, args, setArgs}) => {
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
            return <Card type="Treachery" name={maybeCard} selected={selected} width={100} onClick={()=>{
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

const FactionSelect = ({args, setArgs, config}) => {
    return <Select
      className="basic-single"
      value={{label: args, value: args}}
      options={AllFactions.map((faction)=>{return {label: faction, value: faction}})}
      onChange={(e)=>{setArgs(e.value);}}
      isSearchable={true}
    />;
};

const FremenPlacementSelect = ({args, setArgs, config}) => {
    const [tabr, west, south, westSector, southSector] = args.split(":");
    return (
        <div>
            <h3>Sietch Tabr</h3>
            <Units args={tabr} setArgs={(args)=>{
                setArgs([args, west, south, westSector, southSector].join(":"));
            }} fedaykin={true} />
            <h3>False Wall West</h3>
            <Units args={west} setArgs={(args)=>{
                setArgs([tabr, args, south, westSector, southSector].join(":"));
            }} fedaykin={true} />
            Sector:
            <Integer min={15} max={17} args={westSector} setArgs={(args)=>{
                setArgs([tabr, west, south, args, southSector].join(":"));
            }}/>
            <h3>False Wall South</h3>
            <Units args={south} setArgs={(args)=>{
                setArgs([tabr, west, args, westSector, southSector].join(":"));
            }} fedaykin={true} />
            Sector:
            <Integer min={3} max={4} args={southSector} setArgs={(args)=>{
                setArgs([tabr, west, south, westSector, args].join(":"));
            }}/>
        </div>
    );
};

const RevivalLeader = ({me, args, leaders, setArgs}) => {
    return <PlanLeader leaders={leaders} treachery={[]} selectedLeader={args} setLeader={(leader)=>{
        setArgs(leader);
    }} active={true} canDeselect={true}/>;
};

const RevivalUnits = ({me, args, setArgs, units}) => {
    const hasUnitsSelected = (args.indexOf("1") !== -1) || (args.indexOf("2") !== -1);
    const unitsSelected = hasUnitsSelected ? args.split(",").map((u)=>parseInt(u)).filter((u)=>u) : [];
    const onesSelected = unitsSelected.filter((u)=>u==1).length;
    const twoSelected = unitsSelected.filter((u)=>u==2).indexOf(2) !== -1;

    const twoAvailable = units.indexOf(2) !== -1;
    const numOnesAvailable = Math.min(units.filter((u)=>u==1).length, 3);

    const active = unitsSelected.length < 3;

    let oneSelectors = [];
    for (let i=0; i< numOnesAvailable; i++){
        oneSelectors.push(<UnitSelect key={i} value={1} active={active} selected={i < onesSelected} setSelected={(s)=>{
            const newSelected = Array(onesSelected + (s ? 1 : -1)).fill("1");
            if (twoSelected) { newSelected.push("2"); }
            setArgs(newSelected.join(","));
        }}/>);
    }
    return (
        <div style={{display:"flex"}}>
            {twoAvailable ? <UnitSelect value={2} active={active} selected={twoSelected} setSelected={(s)=>{
                const newSelected = Array(onesSelected).fill("1");
                if (s) { newSelected.push("2"); }
                setArgs(newSelected.join(","));
            }} /> : ""}
            {oneSelectors}
        </div>
    );
};


const Widget = (props) => {
    const {me, state, type, args, config, interaction, setInteraction, clearSelection, updateSelection, setArgs} = props;

    if (type === "null") {
        return "";
    }

    if (type === "choice") {
        return <Choice args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction} updateSelection={updateSelection} clearSelection={clearSelection}/>; 
    }

    if (type === "struct") {
        return <Struct args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction} updateSelection={updateSelection} clearSelection={clearSelection}/>; 
    }

    if (type === "input") {
        return <Input args={args} setArgs={setArgs} config={config} updateSelection/>; 
    }

    if (type === "faction-select") {
        return <FactionSelect args={args} setArgs={setArgs} config={config} />;
    }

    if (type === "constant") {
        return <Constant value={config} setArgs={setArgs} />;
    }

    if (type === "units") {
        return <Units args={args} setArgs={setArgs} fedaykin={config.fedaykin} sardaukar={config.sardaukar}/>;
    }

    if (type === "token-select") {
        return <SelectOnMap mode="token-select" interaction={interaction} setInteraction={setInteraction} setArgs={setArgs} updateSelection={updateSelection} args={args} />;
    }

    if (type === "array") {
        return <ArrayWidget args={args} setArgs={setArgs} config={config}/>;
    }

    if (type === "fremen-placement-select") {
        return <FremenPlacementSelect args={args} setArgs={setArgs} config={config} />;
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

    if (type === "prescience") {
        return <Options options={["leader", "number", "weapon", "defense"]} args={args} setArgs={setArgs} />;
    }

    if (type === "prescience-answer") {
        return <PrescienceAnswer state={state} me={me} args={args} setArgs={setArgs} maxPower={config.max_power} />;
    }

    if (type === "tank-units") {
        return <TankUnits state={state} me={me} args={args} setArgs={setArgs} />;
    }

    if (type === "discard-treachery") {
        return <DiscardTreachery state={state} me={me} args={args} setArgs={setArgs} />;
    }

    if (type === "voice") {
        return <Options options={[
            "poison weapon", "poison defense", "projectile weapon", "projectile defense",
            "no poison weapon", "no poison defense", "no projectile weapon", "no projectile defense",
            "lasgun", "no lasgun"
        ]} args={args} setArgs={setArgs} />;
    }

    if (type === "revival-units") {
        return <RevivalUnits args={args} setArgs={setArgs} units={config.units} />;
    }
    if (type === "revival-leader") {
        return <RevivalLeader args={args} setArgs={setArgs} leaders={config.leaders} />;
    }
    console.warn(type);

    return <span>
        <span>{(type in humanReadable) ? humanReadable[type] : type}:</span>
        <Input args={args} setArgs={setArgs} config={config} />
    </span>;
};

module.exports = Widget;

