import React, {useState} from 'react';

const Command = ({me, faction, cmd}) => {
    return <li className={"history-item" + (faction === me ? " mine" : "") + (faction === "su" ? " su" : "")}>{faction}: {cmd}</li>;
}

export default History = ({showLog, setShowLog, state, error, actions, sendCommand, commandLog, me, interaction, setInteraction, setInteractionFlow, updateSelection, clearSelection}) => {
    const [showSu, setShowSu] = useState(false);
    if (!showLog) {
        return (
            <div className="history" >
                <b onClick={(e)=>{setShowLog(true);}}>Actions Log</b>
            </div>
        );
    }
    return (    
        <div className="history" >
            <div className="log">
                <ul>
                    {commandLog.filter((command)=>{
                        return showSu || command[0] !== "su";
                    }).map((command, i) => <Command key={i} me={me} faction={command[0]} cmd={command[1]}/>)}
                </ul>
            </div>
            <div style={{position:"relative"}} >
                <b onClick={(e)=>{setShowLog(false);}}>Actions Log</b>
                <button className="su-button" onClick={()=>{setShowSu(!showSu);}}>{showSu ? "hide su" : "show su"}</button>
            </div>
        </div>
    );
};
