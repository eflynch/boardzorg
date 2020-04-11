import React from 'react';

import Card from '../components/card';

export default function TraitorSelect({factionState, selected, select}) {
    const cards = factionState.traitors.map((traitor) => {
        const traitorName = traitor[0];
        const onClick = () => {
            select(traitorName);
        };
        return <Card type="Traitor"
                key={"traitor-"+traitorName}
                onClick={() => {select(traitorName);}}
                selected={selected == traitorName}
                name={traitorName}/>;
    });
    return (
        <div style={{display:"flex"}}>
            {cards}
        </div>
    );
};

