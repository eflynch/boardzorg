import React from 'react';

import Card from '../components/card';
import FactionOrder from '../components/faction-order';



export default function Picnick({roundState}) {
    const factions = Object.keys(roundState.proposals);
    return (
        <div style={{display:"flex", flexDirection:"column"}}>
            Alliance Proposals
            {factions.map((faction) => {
                const proposal = roundState.proposals[faction];
                return (
                    <div key={faction}>
                        <b>{faction}:</b> { proposal.length ? proposal.join(" ") : "solo"}
                    </div>
                );
            })}
        </div>
    );
}
