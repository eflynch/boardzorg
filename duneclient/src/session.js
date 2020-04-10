import React, {useState, useEffect} from 'react';
import ReactDOM from 'react-dom';

import Board from './board';
import Faction from './faction';
import History from './history';

import Bidding from './rounds/bidding';
import Battle from './rounds/battle';
import Movement from './rounds/movement';
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


const RoundState = ({roundState, stormPosition, logoPositions, interaction, setInteraction}) => {
    let text = roundState.round + " round";
    if (roundState.stage !== undefined) {
        text += "» " + roundState.stage;
    }
    let stateDiv = null;
    let factionOrder = GetFactionOrder(logoPositions, stormPosition);
    if (roundState && roundState.round == "bidding"){
        stateDiv = <Bidding factionOrder={factionOrder} roundstate={roundState} />;
    }
    if (roundState && roundState.round == "movement"){
        stateDiv = <Movement roundstate={roundState} />;
    }
    if (roundState && roundState.round == "battle"){
        stateDiv = <Battle factionOrder={factionOrder} roundstate={roundState} interaction={interaction} setInteraction={setInteraction} />;
    }
    if (stateDiv === null){
        return (
            <div className="roundstate">
                <h4>{titleCase(text)}</h4>
                {JSON.stringify(roundState)}
            </div>
        );
    }
    return (
        <div className="roundstate">
            <h4>{titleCase(text)}</h4>
            {stateDiv}
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
            backgroundColor: "black",
            alignItems: "center",
            justifyContent: "space-around"
        }}>
            <Deck type="Treachery" facedown={state.treachery_deck} faceup={state.treachery_discard} />
            <Deck type="Spice" facedown={state.spice_deck} faceup={state.spice_discard} />
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
    const [interaction, setInteractionRaw] = useState({
        // Type of selection
        mode: null,
        // Function to call with the selection
        action: null,
    });
    // An object of globally-selected objects, tagged with the interaction mode that selected them
    const [selection, setSelection] = useState({});
    // An list of objects containing interaction modes and actions to perform.
    // This is used to reduce extra clicking on "SelectOnMap" buttons
    const [interactionFlow, setInteractionFlowRaw] = useState([]);

    const [errorState, setErrorState] = useState(error);

    const setInteraction = (interaction) => {
        interaction = maybeFlowInteraction(interaction, selection, interactionFlow);
        const clientAction = interaction.action;
        setInteractionRaw(
            update(interaction,
                   {action: {$set: (...args) => {
                       if (clientAction) {
                           clientAction(...args);
                       }
                       setInteraction({});
                   }}}));
    };

    const setInteractionFlow = (flow) => {
        setInteractionRaw(
            maybeFlowInteraction({}, selection, flow));
        setInteractionFlowRaw(flow);
    };

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
            <div>
                <div style={{display:"flex", alignItems:"flex-start"}}>
                    <Board me={me} interaction={interaction} selection={selection} logoPositions={logoPositions}
                           stormSector={state.storm_position} futureStorm={futureStorm} futureSpice={futureSpice} state={state} />
                    <Decks state={state} />
                </div>
                <RoundState interaction={interaction} selection={selection} roundState={state.round_state} logoPositions={logoPositions} stormPosition={state.storm_position} />
            </div>
            <History state={state} me={me} interaction={interaction} setInteraction={setInteraction} error={errorState} actions={actions} sendCommand={sendCommand} commandLog={history} setInteractionFlow={setInteractionFlow} selection={selection} setSelection={setSelection}/>
            <div className="factions">
                {factions}
            </div>
        </div>
    );
}
