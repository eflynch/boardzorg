import React, {useState, useEffect} from 'react';
import ReactDOM from 'react-dom';

import Board from './board';
import Faction from './faction';
import History from './history';
import Actions from './actions';

import Bidding from './rounds/bidding';
import Battle from './rounds/battle';
import Movement from './rounds/movement';
import Revival from './rounds/revival';
import Nexus from './rounds/nexus';
import Spice from './rounds/spice';
import Deck from './components/deck';
import update from 'immutability-helper';


function titleCase(str) {
  return str.toLowerCase().split(' ').map(function(word) {
    return word.replace(word[0], word[0].toUpperCase());
  }).join(' ');
}

const GetFactionOrder = (logoPositions, stormSector) => {
    const factionOrder = []
    for (let i=0; i<18; i++){
        const sector = (stormSector + i + 1) % 18
        logoPositions.forEach(([name, position]) => {
            if (position === sector) {
                factionOrder.push(name);
            }
        });
    }
    return factionOrder;
};

const GetLogoPositions = (faction_state) => {
    const fs = Object.keys(faction_state);
    return fs.map((faction) => {
        const factionstate = faction_state[faction];
        return [factionstate.name, factionstate.token_position];
    });
}


const RoundState = ({roundState, stormPosition, logoPositions, interaction, selection, winner}) => {
    let text = roundState.round === undefined ? roundState + " round" : roundState.round + " round";
    if (roundState.stage !== undefined) {
        text += "» " + roundState.stage;
    }
    let stateDiv = null;
    let factionOrder = GetFactionOrder(logoPositions, stormPosition);
    if (roundState && roundState.round == "nexus"){
        stateDiv = <Nexus roundState={roundState} />;
    }
    if (roundState && roundState.round == "bidding"){
        stateDiv = <Bidding factionOrder={factionOrder} roundstate={roundState} />;
    }
    if (roundState && roundState.round == "movement"){
        stateDiv = <Movement roundstate={roundState} />;
    }
    if (roundState && roundState.round == "battle"){
        stateDiv = <Battle factionOrder={factionOrder} roundstate={roundState} interaction={interaction} selection={selection}/>;
    }
    if (roundState && roundState.round == "revival") {
        stateDiv = <Revival factionOrder={factionOrder} roundState={roundState} />;
    }
    if (roundState && roundState.round == "spice") {
        stateDiv = <Spice roundState={roundState} />;
    }
    if (roundState == "end") {
        stateDiv = <div className="winner">{winner} Wins!!</div>;
    }
    if (stateDiv === null){
        return (
            <div className="roundstate">
                <h4>{titleCase(text)}</h4>
            </div>
        );
    }
    return (
        <div className="roundstate">
            <h4>{titleCase(text)}</h4>
            <div style={{backgroundColor: "black", padding: 5}}>
                {stateDiv}
            </div>
        </div>
    );
};


const Decks = ({state}) => {
    return (
        <div style={{
            display:"flex",
            flexDirection:"column",
            flexWrap: "wrap",
            flexGrow: 1,
            alignSelf: "stretch",
            alignItems: "center",
            justifyContent: "space-around",
            paddingRight: 10
        }}>
        </div>
    );
};

const maybeFlowInteraction = (interaction, selection, flows) => {
    if (interaction.mode == null) {
        for (const flow of flows) {
            if (selection[flow.mode] == null) {
                return flow;
            }
        }
    }
    return interaction;
};

export default function Session({state, actions, history, me, error, sendCommand}) {
    const [combinedState, setCombinedState] = useState({
        interaction: {},
        selection: {},
        interactionFlow: [],
    });

    const interaction = combinedState.interaction;
    const selection = combinedState.selection;

    const clearSelection = () => {
        setCombinedState((combinedState) => {
            return update(combinedState, {selection: {$set: {}}});
        });
    };

    const updateSelection = (mode, value) => {
        if (value && value != "-") {
            setCombinedState((combinedState) => {
                return update(combinedState, {
                    selection: {
                        [mode]: {$set: value}
                    }
                });
            });
        } else {
            setCombinedState((combinedState) => {
                return update(combinedState, {
                    selection: {
                        $unset: [mode]
                    }
                });
            });
        }
    };

    const wrapInteraction = (interaction, combinedState) => {
        let newInteraction = maybeFlowInteraction(
            interaction,
            combinedState.selection,
            combinedState.interactionFlow);
        const clientAction = newInteraction.action;
        return update(
            newInteraction,
            {action: {$set: (...args) => {
                if (clientAction) {
                    clientAction(...args);
                }
                setInteraction({});
            }}});
    };

    const setInteraction = (interaction) => {
        setCombinedState((combinedState) => {
            return update(combinedState,
                          {interaction: {$set: wrapInteraction(interaction, combinedState)}});
        });
    };


    const setInteractionFlow = (flow) => {
        setCombinedState((combinedState) => {
            const updatedState = update(combinedState, {interactionFlow: {$set: flow}});
            return update(updatedState,
                          {interaction: {$set:wrapInteraction({}, updatedState)}});
        });
    };

    const [errorState, setErrorState] = useState(error);
    const [showLog, setShowLog] = useState(false);

    useEffect(()=>{
        if (error !== undefined) {
            setErrorState(error);
        } else {
            const timeout = setTimeout(()=> {
                setErrorState(undefined);
            }, 5000);
            return () => {
                clearTimeout(timeout);
            }
        }
    }, [error])

    const fs = Object.keys(state.faction_state).sort((x,y)=>{ return x == me ? -1 : y == me ? 1 : 0; });;

    const factions = fs.map((faction)=> {
        return <Faction key={faction} me={me} faction={faction} factionstate={state.faction_state[faction]} selection={selection}/>;
    });

    let futureStorm = undefined;
    if (state.storm_deck.next !== undefined) {
        futureStorm = (state.storm_deck.next + state.storm_position) % 18;
    }
    let futureSpice = undefined;
    if (state.spice_deck.next !== undefined) {
        futureSpice = state.spice_deck.next;
    }
    const logoPositions = GetLogoPositions(state.faction_state);

    return (
        <div className="session">
            <div className="board-layer">
                <div style={{
                    padding: 10,
                    borderRadius: 4,
                    textAlign: "center",
                    minWidth: 350,
                    maxWidth: 550,
                    backgroundColor: "white",
                    margin: 20
                }}>
                    <RoundState interaction={interaction} selection={selection} roundState={state.round_state} logoPositions={logoPositions} stormPosition={state.storm_position} winner={state.winner} />
                    <Actions me={me} state={state} interaction={interaction} setInteraction={setInteraction} error={errorState} actions={actions} sendCommand={sendCommand} setInteractionFlow={setInteractionFlow} updateSelection={updateSelection} clearSelection={clearSelection}/>
                </div>
                <div style={{display:"flex"}}>
                    <Board me={me} interaction={interaction} selection={selection} logoPositions={logoPositions}
                           stormSector={state.storm_position} futureStorm={futureStorm} futureSpice={futureSpice} state={state} />
                    <div style={{display:"flex", flexDirection:"column", justifyContent:"space-between"}}>
                        <Deck type="Treachery" facedown={state.treachery_deck} faceup={state.treachery_discard} />
                        <Deck type="Spice" facedown={state.spice_deck} faceup={state.spice_discard} />
                    </div>
                </div>
            </div>
            <History showLog={showLog} setShowLog={setShowLog} state={state} me={me} setInteraction={setInteraction} commandLog={history} />
            <div className="factions">
                {factions}
            </div>
        </div>
    );
}
