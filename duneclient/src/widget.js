import React, {useState} from 'react';
import Select from 'react-select';
import Slider, { Range } from 'rc-slider';
import update from 'immutability-helper';


const AllFactions = ["emperor", "fremen", "guild", "bene-gesserit", "harkonnen", "atreides"];

const Choice = ({args, setArgs, config, ...props}) => {
    return (
        <div>
            {config.map((subWidget, i) => {
                return (
                    <div key={i}>
                        <Widget {...props} key={i} type={subWidget.widget} config={subWidget.args} args={args} setArgs={setArgs}/>
                    </div>
                );
            })}
        </div>
    );
};

const Struct = ({args, setArgs, config, ...props}) => {
    const subArgs = args.split(" ");
    return (
        <div>
            {config.map((subWidget, i) => {
                return <Widget {...props} key={i} type={subWidget.widget} config={subWidget.args} setArgs={(args)=> {
                    const newSubArgs = update(subArgs, {[i]: {$set: args}});
                    setArgs(newSubArgs.join(" "));
                }} args={subArgs[i]} />
            })}
        </div>
    );
};

const ArrayWidget = ({args, setArgs, config}) => {
    const subArgs = args.split(":");
    let widgets = subArgs.map((arg, i) => {
        return <Widget key={i} type={config.widget} config={config.args} args={arg} setArgs={(args)=> {
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


const SelectOnMap = ({args, setArgs, interaction, setInteraction, mode}) => {
    let pieces;
    if (interaction.mode === mode) {
        if (interaction[mode] === null) {
            pieces = <div className="select-on-map on">Select on Board</div>;
        } else {
            pieces = [
                <div key="select" className="select-on-map on" onClick={(e)=>{
                    setArgs(`$interaction.${mode}`);
                    setInteraction(update(interaction, {
                        [mode]: {$set: null}
                    }));
                }}>Select on Board</div>,
                <div key="value">Selected: {interaction[mode]}</div>
            ];
        }
    } else {
        pieces = [
            <div key="select" className="select-on-map off" onClick={(e)=>{
                setArgs(`$interaction.${mode}`);
                setInteraction(update(interaction, {
                    mode: {$set: mode},
                    [mode]: {$set: null}
                }));
            }}>Select on Board</div>
        ];
        if (interaction[mode]) {
            pieces.push(<div key="value">Selected: {interaction[mode]}</div>);
        }
    }
    return (
        <div style={{display:"flex", flexDirection: "column", alignItems:"center"}}>
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

const Units = ({args, setArgs, fedaykin, sardaukar}) => {
    const units = args.split(",").map((i)=>parseInt(i));
    const numOnes = units.filter((i)=>i===1).length;
    const numTwos = units.filter((i)=>i===2).length;

    let bonus = <div/>;
    if (fedaykin || sardaukar) {
        bonus = (
            <div style={{display: "flex"}}>
                <div className="label">{fedaykin ? "Fedaykin: " : "Sardaukar: "}{numTwos}</div>
                <Slider min={0} max={fedaykin ? 3 : 5} step={1} dots={true} value={numTwos}
                    onChange={(value)=>{
                        const ones = Array(numOnes).fill("1").join(",");
                        const twos = Array(value).fill("2").join(",");
                        if (ones && twos){
                            setArgs([ones, twos].join(","));
                        } else {
                            setArgs(ones + twos);
                        }
                    }} />
            </div>
        );
    }
    return (
        <div className="unit-select">
            <div style={{display: "flex"}}>
                <div className="label">Units: {numOnes}</div>
                <Slider min={0} max={20} step={1} dots={true} value={numOnes}
                    onChange={(value)=>{
                        const ones = Array(value).fill("1").join(",");
                        const twos = Array(numTwos).fill("2").join(",");
                        if (ones && twos){
                            setArgs([ones, twos].join(","));
                        } else {
                            setArgs(ones + twos);
                        }
                    }} />
            </div>
            {bonus} 
        </div>
    );
};

const Integer = ({args, setArgs, type, min, max}) => {
    return (
        <div>
            {args} {type ? type : ""}
            <Slider min={min} max={max} step={1} value={parseInt(args)}
                onChange={(value)=>{
                    setArgs(value.toString());
            }} />
        </div>
    );
};


const Widget = ({type, args, setArgs, config, interaction, setInteraction}) => {
    if (type === "null") {
        return "";
    }

    if (type === "choice") {
        return <Choice args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction}/>; 
    }

    if (type === "struct") {
        return <Struct args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction}/>; 
    }

    if (type === "input") {
        return <Input args={args} setArgs={setArgs} config={config}/>; 
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
        return <SelectOnMap mode="token-select" interaction={interaction} setInteraction={setInteraction} setArgs={setArgs} />;
    }

    if (type === "array") {
        return <ArrayWidget args={args} setArgs={setArgs} config={config} />;
    }

    if (type === "fremen-placement-select") {
        return <FremenPlacementSelect args={args} setArgs={setArgs} config={config} />;
    }

    if (type === "integer") {
        return <Integer args={args} setArgs={setArgs} type={config.type} min={config.min} max={config.max} />;
    }

    if (type === "space-select") {
        return <SelectOnMap mode="space-select" args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction}/>;
    }

    if (type === "space-sector-select-start") {
        return <SelectOnMap mode="space-sector-select-start" args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction}/>;
    }

    if (type === "space-sector-select-end") {
        return <SelectOnMap mode="space-sector-select-end" args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction}/>;
    }

    if (type === "traitor-select") {
        return <SelectOnMap mode="traitor-select" interaction={interaction} setInteraction={setInteraction} setArgs={setArgs}/>;
    }

    if (type === "battle-select") {
        return <SelectOnMap mode="battle-select" interaction={interaction} setInteraction={setInteraction} setArgs={setArgs}/>;
    }


    console.log(type);
    return <Input args={args} setArgs={setArgs} config={config} />;
};

module.exports = Widget;

