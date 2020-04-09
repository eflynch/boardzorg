import React, {useState} from 'react';
import update from 'immutability-helper';

import Widget from './widget';


const interactionWidgets = [
    "token-select",
    "space-sector-select",
    "space-sector-select-start",
    "space-sector-select-end",
    "sector-select",
    "space-select",
    "traitor-select",
    "leader-input",
    "battle-select",
];

const defaultArgsForAction = (state, actionName, argSpec) => {
    if (actionName === "bribe") {
        return "emperor 2";
    }
    if (actionName === "gift") {
        return "fremen 2";
    }

    if (actionName === "fremen-placement") {
        return ":::16:3";
    }
    if (actionName === "movement-select") {
        return "   ";
    }
    if (actionName === "commit-plan") {
        return " 0 - -";
    }
    if (actionName === "answer-prescience") {
        const prescience_query = state.round_state.stage_state.prescience;
        if (prescience_query === "leader") {
            return "";
        } else if (prescience_query === "number") {
            return "0";
        } else {
            return "-";
        }
    }

    if (interactionWidgets.indexOf(argSpec.widget) !== -1) {
        return `$interaction.${argSpec.widget}`;
    }

    if (argSpec.widget === "struct") {
        let subArgs = [];
        for (const subWidget of argSpec.args) {
            subArgs = subArgs.concat(defaultArgsForAction(state, actionName, subWidget));
        }
        return subArgs.join(" ");
    }

    return "";
};

const ActionArgs = ({me, state, args, setArgs, sendCommand, actionName, argSpec, interaction, setInteraction}) => {
    return (
        <div>
            <Widget
                me={me}
                state={state}
                interaction={interaction}
                setInteraction={setInteraction}
                setArgs={setArgs}
                args={args}
                type={argSpec.widget}
                config={argSpec.args} />
            <br/>
            <br/>
            <button disabled={interaction.mode != null} onClick={()=>{
                const fixedArgs = args.split(" ").map((arg) => {
                    if (arg.startsWith("$")) {
                        return interaction[arg.slice(13)];
                    }
                    return arg;
                }).join(" ");
                sendCommand(`${actionName} ${fixedArgs}`);
                setInteraction({mode: null});
            }}>Submit Command</button>
        </div>
    );
} 


const getFlowForWidget = (type, config) => {
    if (interactionWidgets.indexOf(type) !== -1) {
        return [type];
    }

    if (type === "struct") {
        let ret = [];
        for (const subWidget of config) {
            ret = ret.concat(getFlowForWidget(subWidget.widget, subWidget.args));
        }
        console.log(ret);
        return ret;
    }
    return [];
};

/*
Actions manages a list of space separated args " " which can be submitted as a command.

It creates widgets for each arg based on the selected action type.

interaction and setInteraction are used for situations where these widgets
need to interact with global state.

Both these widgets as well as other interactive objects like the board are expected
to handle interaction and setInteraction based on a reasonable protocol.

Since the state of the selected args is rooted here and is not global,
if the result of the interaction will be needed at command submit time, we can use
the arg $interaction.[some prop] to retrieve it at submit time.

Additionally, we compute whether an interaction is on-going from the current
interaction state and disable the submit button if it is
to ensure that all $interaction props will be present at submit time.

*/

const Actions = (props) => {
    const [args, setArgs] = useState("");
    const [selectedAction, setSelectedAction] = useState(null);

    let {me, state, error, actions, sendCommand, setInteraction, setInteractionFlow, interaction} = props;
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
                setArgs(defaultArgsForAction(state, actionName, actions[actionName]));
                setInteractionFlow(getFlowForWidget(actions[actionName].widget, actions[actionName].args));
            }} key={i}>
                {actionName}
            </li>
        );
    });
    let actionArgs = <span/>;
    if (actionNames.indexOf(selectedAction) != -1) {
        actionArgs = <ActionArgs me={me} state={state} args={args} setArgs={setArgs} interaction={interaction} setInteraction={setInteraction} sendCommand={sendCommand} actionName={selectedAction} argSpec={actions[selectedAction]}/>
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
