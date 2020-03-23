import React from 'react';

import Actions from './actions';

export default History = ({stageTitle, error, actions, sendCommand, commandLog, faction}) => {
    return (
        <div className="history">
            <div className="stage-title"><b>Stage</b>: {stageTitle}</div>
            <div>Available Actions</div>
            <Actions error={error} actions={actions} sendCommand={sendCommand}/>
            <div>Actions Log</div>
            <div className="log">
                <ul>
                    {commandLog.map((command, i) => <li key={i}>{command[0]}: {command[1]}</li>)}
                </ul>
            </div>
        </div>
    );
};
