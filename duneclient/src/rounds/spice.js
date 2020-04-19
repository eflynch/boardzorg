import React from 'react';

import FactionOrder from '../components/faction-order';

export default function Spice({roundState}) {
    if (!roundState.stage_state || roundState.stage_state.stage !== "worm") {
        return [];
    }

    return <FactionOrder factions={roundState.stage_state.factions.map((faction)=>{
        return {
            faction: faction,
            active: faction === roundState.stage_state.faction_turn
        };
    })} />;
};

