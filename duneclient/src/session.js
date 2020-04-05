import React, {useState, useEffect} from 'react';
import ReactDOM from 'react-dom';

import Board from './board';
import Faction from './faction';
import History from './history';

import Bidding from './rounds/bidding';
import Movement from './rounds/movement';
import Deck from './components/deck';
import update from 'immutability-helper';

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


const RoundState = ({roundState, stormPosition, logoPositions}) => {
    let stateDiv = null;
    let factionOrder = GetFactionOrder(logoPositions, stormPosition);
    if (roundState && roundState.round == "bidding"){
        stateDiv = <Bidding factionOrder={factionOrder} roundstate={roundState} />;
    }
    if (roundState && roundState.round == "movement"){
        stateDiv = <Movement roundstate={roundState} />;
    }
    if (stateDiv === null){
        return <div className="roundstate">{JSON.stringify(roundState)}</div>;
    }
    return <div className="roundstate">{stateDiv}</div>;
};


const Decks = ({state}) => {
    console.log(state);
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

const maybeFlowInteraction = (interaction, flow) => {
    if (!interaction.mode) {
        for (const mode of flow) {
            if (interaction[mode] == null) {
                return update(interaction, {
                    mode: {$set: mode}
                });
            }
        }
    }
    return interaction;
};

export default function Session({state, actions, history, me, error, sendCommand}) {
    const [interaction, setInteractionRaw] = useState({mode: null});
    const [errorState, setErrorState] = useState(error);
    const [interactionFlow, setInteractionFlowRaw] = useState([]);

    const setInteraction = (interaction) => {
        setInteractionRaw(maybeFlowInteraction(interaction, interactionFlow));
    };

    const setInteractionFlow = (flow) => {
        setInteractionRaw(
            maybeFlowInteraction(
                update(
                    interaction,
                    {mode: {$set: null}}),
                flow));
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
        return <Faction key={faction} me={me} faction={faction} factionstate={state.faction_state[faction]}/>;
    });

    let futureStorm = undefined;
    if (state.storm_deck.next !== undefined) {
        futureStorm = (state.storm_deck.next + state.storm_position) % 18;
    }
    const logoPositions = GetLogoPositions(state.faction_state);
    return (
        <div className="session">
            <div>
                <div style={{display:"flex", alignItems:"flex-start"}}>
                    <Board me={me} interaction={interaction} setInteraction={setInteraction} logoPositions={logoPositions}
                           stormSector={state.storm_position} futureStorm={futureStorm} state={state} />
                    <Decks state={state} />
                </div>
                <RoundState roundState={state.round_state} logoPositions={logoPositions} stormPosition={state.storm_position} />
            </div>
            <History interaction={interaction} setInteraction={setInteraction} error={errorState} actions={actions} sendCommand={sendCommand} commandLog={history} setInteractionFlow={setInteractionFlow}/>
            <div className="factions">
                {factions}
            </div>
        </div>
    );
}
