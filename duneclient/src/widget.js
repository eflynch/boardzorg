import React, {useState} from 'react';
import Select from 'react-select';
import update from 'immutability-helper';


const AllFactions = ["emperor", "fremen", "guild", "bene-gesserit", "harkonnen", "atreides"];

const Choice = ({args, setArgs, config}) => {
    return (
        <div>
            {config.map((subWidget, i) => {
                return (
                    <div>
                        <Widget key={i} type={subWidget.widget} config={subWidget.args} args={args} setArgs={setArgs}/>
                    </div>
                );
            })}
        </div>
    );
};

const Struct = ({args, setArgs, config}) => {
    const [subArgs, setSubArgs] = useState(args.split(" "));
    return (
        <div>
            {config.map((subWidget, i) => {
                return <Widget key={i} type={subWidget.widget} config={subWidget.args} setArgs={(args)=> {
                    const newSubArgs = update(subArgs, {[i]: {$set: args}});
                    setSubArgs(newSubArgs);
                    setArgs(newSubArgs.join(" "));
                }} args={subArgs[i]} />
            })}
        </div>
    );
};

const Input = ({args, setArgs, config}) => {
    return <input value={args} onChange={((e)=>{
        const value = e.target.value;
        setArgs(value);
    })}/>;
};


const TokenSelect = ({args, setArgs, interaction, setInteraction}) => {
    let pieces;
    if (interaction.mode === "token-select") {
        if (interaction.selected === null) {
            pieces = <div className="token-select on">Select on Map</div>;
        } else {
            pieces = [
                <div key="select" className="token-select" onClick={(e)=>{
                    setArgs("$interaction.selected");
                    setInteraction(update(interaction, {
                        selected: {$set: null}
                    }));
                }}>Select on Map</div>,
                <div key="value">Selected Position: {interaction.selected}</div>
            ];
        }
    } else {
        pieces = <div className="token-select off" onClick={(e)=>{
            setArgs("$interaction.selected");
            setInteraction(update(interaction, {
                mode: {$set: "token-select"},
                selected: {$set: null}
            }));
        }}>Select on Map</div>;
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


const Widget = ({type, args, setArgs, config, interaction, setInteraction}) => {
    if (type === "choice") {
        return <Choice args={args} setArgs={setArgs} config={config}/>; 
    }

    if (type === "struct") {
        return <Struct args={args} setArgs={setArgs} config={config}/>; 
    }

    if (type === "input") {
        return <Input args={args} setArgs={setArgs} config={config}/>; 
    }

    if (type === "faction-select") {
        return <FactionSelect args={args} setArgs={setArgs} config={config} />;
    }

    if (type === "integer") {
        return <Input args={args} setArgs={setArgs} config={config}/>;
    }

    if (type === "constant") {
        return args;
    }

    if (type === "units") {
        return <Input args={args} setArgs={setArgs} config={config}/>;
    }

    if (type === "space-sector-select") {
        return <Input args={args} setArgs={setArgs} config={config}/>;
    }

    if (type === "token-select") {
        return <TokenSelect interaction={interaction} setInteraction={setInteraction} setArgs={setArgs} />;
    }

    if (type === "leader-input") {
        return <Input args={args} setArgs={setArgs} config={config} />;
    }

    console.log(type);
};

module.exports = Widget;

