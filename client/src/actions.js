import React, {useState, useEffect} from 'react';
import update from 'immutability-helper';

import Widget from './widget';


const interactionWidgets = [
    "token-select",
    "space-sector-select",
    "space-sector-select-start",
    "space-sector-select-end",
    "sector-select",
    "space-select",
    "character-input",
    "battle-select",
];

const defaultArgsForAction = (state, me, actionName, argSpec) => {
    if (actionName === "bribe" || actionName === "gift") {
        const factions = Object.keys(state.faction_state).filter(f => f !== me);
        return [factions.length ? factions[0] : me, "2"];
    }

    if (actionName === "christopher_robbin-placement") {
        return ":::16:3";
    }
    if (actionName === "movement-select") {
        return "   ";
    }
    if (actionName === "commit-plan") {
        const stageState = state.round_state.stage_state;
        const [attacker, defender, space, sector] = stageState.battle;
        const iAmAttacker = me === attacker;
        const mePlan = iAmAttacker ? stageState.attacker_plan : stageState.defender_plan;

        const defaultArg =`${mePlan.character ? mePlan.character[0] : "-"} ${mePlan.number ? mePlan.number : "0"} ${mePlan.weapon ? mePlan.weapon : "-"} ${mePlan.defense ? mePlan.defense : "-"} -`;
        return defaultArg;
    }
    if (actionName === "answer-flight") {
        const flight_query = state.round_state.stage_state.flight;
        if (flight_query === "character") {
            return "";
        } else if (flight_query === "number") {
            return "0";
        } else {
            return "-";
        }
    }

    if (argSpec.widget === "retrieval-character") {
        return "-";
    }

    if (argSpec.widget === "struct") {
        let subArgs = [];
        for (const subWidget of argSpec.args) {
            subArgs = subArgs.concat(defaultArgsForAction(state, me, actionName, subWidget));
        }
        return subArgs;
    }

    return "";
};

const ActionArgs = ({me, state, args, setArgs, sendCommand, actionName, argSpec, interaction, setInteraction, updateSelection, clearSelection, setSelectedAction}) => {
    return (
        <div>
            <Widget
                me={me}
                state={state}
                interaction={interaction}
                setInteraction={setInteraction}
                setArgs={setArgs}
                clearSelection={clearSelection}
                updateSelection={updateSelection}
                args={args}
                type={argSpec.widget}
                config={argSpec.args} />
            <br/>
            <br/>
            <button disabled={interaction.mode != null} onClick={()=>{
                sendCommand(`${actionName} ${[args].flat(Infinity).join(" ")}`);
                clearSelection();
                setInteraction({});
                setSelectedAction(null);
            }}>Submit Command</button>
        </div>
    );
}


const getFlowForWidget = (type, config, setArgs, updateSelection) => {
    if (interactionWidgets.indexOf(type) !== -1) {
        const flow = [{
            mode: type,
            action: (val) => {
                updateSelection(type, val);
                setArgs(val);
            },
        }];
        return flow;
    }

    if (type === "struct") {
        let ret = [];
        for (const [i, subWidget] of config.entries()) {
            const setSubArgs = (newSubArgs) => {
                setArgs((args) => {
                    return update(args, {[i]: {$set: newSubArgs}});
                });
            };
            ret = ret.concat(getFlowForWidget(subWidget.widget, subWidget.args, setSubArgs, updateSelection));
        }
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


const passStubs = [
    "author-pass-",
    "pass-"
];

const Actions = (props) => {
    const [args, setArgs] = useState("");
    const [selectedAction, setSelectedAction] = useState(null);
    const [autoPass, setAutoPass] = useState(true);

    let {me, state, error, actions, sendCommand, setInteraction, setInteractionFlow,
         interaction, updateSelection, clearSelection} = props;

    const actionNames = actions.map((action)=>action.name); 
    useEffect(()=> {
        let timeoutID = false;
        if (autoPass) {
            actionNames.forEach((action) => {
                passStubs.forEach((stub) => {
                    if (action.startsWith(stub)) {
                        if (!actionNames.filter(testAction=>testAction.startsWith(action.replace(stub, ""))).length) {
                            timeoutID = setTimeout(()=>{
                                sendCommand(action);
                            }, 500);
                        }
                    }
                });
            });
        }
        return () => {
            if (timeoutID) {
                clearTimeout(timeoutID);
            }
        }
    });

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
    const actionButtons = actions.map(({name, spec, blocking}, i) => {
        return (
            <li className={selectedAction === name ? "selected" : ""} key={i} onClick={()=>{
                setSelectedAction(name);
                clearSelection();
                setArgs(defaultArgsForAction(state, me, name, spec));
                setInteractionFlow(getFlowForWidget(spec.widget, spec.args, setArgs, updateSelection));
            }} key={i}>
                {name}
            </li>
        );
    });
    let actionArgs = <span/>;
    if (actionNames.indexOf(selectedAction) != -1) {
        const argSpec = actions[actionNames.indexOf(selectedAction)].spec;
        actionArgs = <ActionArgs me={me} state={state} args={args} setArgs={setArgs} interaction={interaction} setInteraction={setInteraction} sendCommand={sendCommand} actionName={selectedAction} argSpec={argSpec} updateSelection={updateSelection} clearSelection={clearSelection} setSelectedAction={setSelectedAction}/>
    }
    return (
        <div>
            <div style={{position:"relative"}}>
                <b>Available Actions</b>
                <button className="su-button" onClick={()=>{setAutoPass(!autoPass);}}>{autoPass ? "✅ auto pass" : "⬛️ auto pass"}</button>
            </div>
            <div className="actions-wrapper">
                <div className="actions">
                    {actionButtons}
                </div>
                {actionArgs}
                {errordiv}
            </div>
        </div>
    );
}

module.exports = Actions;
