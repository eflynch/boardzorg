import React, {useState} from 'react';
import update from 'immutability-helper';

const Logo = ({faction, diameter, ...props}) => {
    return <img {...props} src={`/static/app/png/${faction}_logo.png`} width={diameter} height={diameter}/>;
}; 

const ALL_FACTIONS = {"atreides": true, "harkonnen": true, "fremen": true, "bene-gesserit": true, "emperor": true, "guild": true};


const FactionSelector = ({faction, selected, diameter, onSelect}) => {
    return (
        <Logo className={"select-faction" + (selected ? " selected" : "")} onClick={onSelect} faction={faction} diameter={diameter} />
    );
}


export default function SessionCreator({newSession}) {
    const [selectedFactions, setSelectedFactions] = useState(ALL_FACTIONS);
    const [name, setName] = useState("");

    let factions = Object.keys(ALL_FACTIONS);
    factions.sort();
    const factionSelectors = factions.map((faction)=> {
        const selected = selectedFactions[faction];
        return <FactionSelector diameter={100} key={faction} faction={faction} selected={selected} onSelect={()=>{
            setSelectedFactions(update(selectedFactions, {[faction]: {$set: !selected}}))
        }}/>;
    });

    return (
        <div className="sessioncreator">
            <input value={name} onChange={(e)=>{
                setName(e.target.value);
            }}/>
            <div style={{display:"flex", justifyContent:"space-around", flexWrap:"wrap"}}>
                {factionSelectors}
            </div>
            <button onClick={()=>{newSession(name, Object.keys(selectedFactions).filter((f)=>selectedFactions[f]))}}>Create Session</button>
        </div>
    );
}

module.exports = SessionCreator;
