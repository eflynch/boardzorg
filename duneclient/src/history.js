import React from 'react';

import Actions from './actions';

export default History = ({error, actions, sendCommand, commandLog, faction, interaction, setInteraction}) => {
    return (    
        <div className="history">
            <b>Available Actions</b>
            <Actions interaction={interaction} setInteraction={setInteraction} error={error} actions={actions} sendCommand={sendCommand}/>
            <br/>
            <b>Actions Log</b>
            <div className="log">
                <ul>
                    {commandLog.map((command, i) => <li key={i}>{command[0]}: {command[1]}</li>)}
                </ul>
            </div>
            <button onClick={()=>{sendCommand("undo");}}>undo</button>
        </div>
    );
};
