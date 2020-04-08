import React from 'react';

import LeaderToken from '../components/leader-token';
import Units from './units';

export default function BattlePlan({me, state, args, setArgs, interaction, setInteraction}) {
    const stageState = state.round_state.stage_state;
    const meFactionState = state.faction_state[me];
    const [attacker, defender, space, sector] = stageState.battle;
    const meMaxUnits = state.map_state.filter(s=>s.name === space)[0].forces[me][sector].reduce((a,b)=>a+b, 0);
    const iAmAttacker = me === attacker;
    const mePlan = iAmAttacker ? stageState.attacker_plan : stageState.defender_plan;
    const [selectedLeader, selectedUnits, selectedWeapon, selectedDefense] = args.split(" ");

    const meLeaders = meFactionState.leaders.map((leader) => {
        const [name, power] = leader;
        const selected = (mePlan.leader !== undefined && mePlan.leader[0] === name) || selectedLeader === name;
        let onClick = undefined;
        if (mePlan.leader === undefined) {
            onClick = ()=> {
                const newArgs = [name, selectedUnits, selectedWeapon, selectedDefense].join(" ");
                setArgs(newArgs); 
            };
        }
        return <LeaderToken
                    key={name}
                    name={name}
                    selected={selected}
                    dead={false} onClick={onClick}/>;
    });

    return (
        <div className="battle-plan">
            {meLeaders}
            <Units maxOnes={meMaxUnits} args={Array(parseInt(selectedUnits)).fill("1").join(",")} setArgs={(units)=>{
                const newArgs = [selectedLeader, units.split(",").length, selectedWeapon, selectedDefense].join(" ");
                setArgs(newArgs);
            }} />
        </div>
    );
}