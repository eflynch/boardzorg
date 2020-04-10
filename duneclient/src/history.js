import React, {useState} from 'react';

import Actions from './actions';

const Command = ({me, faction, cmd}) => {
    return <li className={"history-item" + (faction === me ? " mine" : "") + (faction === "su" ? " su" : "")}>{faction}: {cmd}</li>;
}

export default History = ({state, error, actions, sendCommand, commandLog, me, interaction, setInteraction, setInteractionFlow, selection, setSelection}) => {
    const [showSu, setShowSu] = useState(false);
    return (    
        <div className="history">
            <b>Available Actions</b>
            <Actions me={me} state={state} interaction={interaction} setInteraction={setInteraction} error={error} actions={actions} sendCommand={sendCommand} setInteractionFlow={setInteractionFlow} selection={selection} setSelection={setSelection}/>
            <br/>
            <div style={{position:"relative"}}>
                <b>Actions Log</b>
                <button className="su-button" onClick={()=>{setShowSu(!showSu);}}>{showSu ? "hide su" : "show su"}</button>
            </div>
            <div className="log">
                <ul>
                    {commandLog.filter((command)=>{
                        return showSu || command[0] !== "su";
                    }).map((command, i) => <Command key={i} me={me} faction={command[0]} cmd={command[1]}/>)}
                </ul>
            </div>
        </div>
    );
};
