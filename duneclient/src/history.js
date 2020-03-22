import React from 'react';

import Actions from './actions';

export default History = ({stageTitle, error, actions, sendCommand, commandLog}) => {
    return (
        <div className="history">
            {stageTitle}
            <Actions error={error} actions={actions} sendCommand={sendCommand}/>
            <ul>
                {commandLog.map((command, i) => <li key={i}>{command[0]}: {command[1]}</li>)}
            </ul>
        </div>
    );
};
