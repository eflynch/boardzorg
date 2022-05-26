import React, {useState} from 'react';

const Command = ({me, faction, cmd}) => {
    return <li className={
        "history-item" +
        (faction === me ? " mine" : "") +
        (faction === "su" ? " su" : "") +
        (cmd.includes("chat") ? " chat" : "")
    }><span>{faction}:</span> {cmd.replace("chat ", "")}</li>;
}

export default History = ({showLog, setShowLog, state, error, actions, sendCommand, commandLog, me, interaction, setInteraction, setInteractionFlow, updateSelection, clearSelection}) => {
    const [showSu, setShowSu] = useState(false);
    if (!showLog) {
        return (
            <div className="menu history" >
                <b className="menu-toggle" onClick={(e)=>{setShowLog(true);}}>Actions Log</b>
            </div>
        );
    }
    return (    
        <div className="menu history" >
            <b className="menu-toggle" onClick={(e)=>{setShowLog(false);}}>Actions Log</b>
            <div style={{display:'flex', flexDirection:'column'}}>
                <b className="su-button" onClick={()=>{setShowSu(!showSu);}}>{showSu ? "hide auto" : "show auto"}</b>
                <div className="log">
                    <ul>
                        {commandLog.filter((command)=>{
                            return showSu || command[0] !== "su";
                        }).reverse().map((command, i) => <Command key={i} me={me} faction={command[0]} cmd={command[1]}/>)}
                    </ul>
                </div>
            </div>
        </div>
    );
};
