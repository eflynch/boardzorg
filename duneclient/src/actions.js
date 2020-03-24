import React, {useState} from 'react';
import update from 'immutability-helper';

import {isInteractionInProcess} from './interaction';
import Widget from './widget';

const defaultArgsForAction = (actionName) => {
    if (actionName === "bribe") {
        return "emperor 2";
    }
    return "";
};

const ActionArgs = ({args, setArgs, sendCommand, actionName, argSpec, interaction, setInteraction}) => {
    return (
        <div>
            <Widget
                interaction={interaction}
                setInteraction={setInteraction}
                setArgs={setArgs}
                args={args}
                type={argSpec.widget}
                config={argSpec.args} />
            <br/>
            <button disabled={isInteractionInProcess(interaction, argSpec.widget)} onClick={()=>{
                const fixedArgs = args.split(" ").map((arg) => {
                    if (arg.startsWith("$")) {
                        return interaction[arg.slice(13)];
                    }
                    return arg;
                }).join(" ");
                sendCommand(`${actionName} ${fixedArgs}`);
            }}>Submit Command</button>
        </div>
    );
} 

const Actions = (props) => {
    const [args, setArgs] = useState("");
    const [selectedAction, setSelectedAction] = useState(null);

    let {error, actions, sendCommand, setInteraction, interaction} = props;
    let errordiv = <div/>;
    if (error !== null && error !== undefined){
        if (error.BadCommand !== undefined){
            errordiv = <div className="error">{error.BadCommand}</div>;
        }
        if (error.IllegalAction !== undefined){
            errordiv = <div className="error">{error.IllegalAction}</div>;
        }
        if (error.UnhandledError !== undefined){
            errordiv = <div className="error">{error.UnhandledError}</div>;
        }
    }
    const actionNames = Object.keys(actions);
    const actionButtons = actionNames.map((actionName, i) => {
        return (
            <li className={selectedAction === actionName ? "selected" : ""} key={i} onClick={()=>{
                setSelectedAction(actionName);
                setArgs(defaultArgsForAction(actionName));
                setInteraction({mode: null});
            }} key={i}>
                {actionName}
            </li>
        );
    });
    let actionArgs = <span/>;
    if (actionNames.indexOf(selectedAction) != -1) {
        actionArgs = <ActionArgs args={args} setArgs={setArgs} interaction={interaction} setInteraction={setInteraction} sendCommand={sendCommand} actionName={selectedAction} argSpec={actions[selectedAction]}/>
    }
    return (
        <div className="actions-wrapper">
            <div className="actions">
                {actionButtons}
            </div>
            {actionArgs}
            {errordiv}
        </div>
    );
}

module.exports = Actions;
