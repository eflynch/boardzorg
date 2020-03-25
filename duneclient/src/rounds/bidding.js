import React from 'react';

import TreacheryCard from '../components/treachery-card';

const getFactionOrder = (roundstate, logoPositions, stormSector) => {
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

const Logo = ({faction, diameter, x, y, ...props}) => {
    return <image {...props} xlinkHref={`/static/app/png/${faction}_logo.png`} x={x} y={y} width={diameter} height={diameter}/>;
};

const FactionOrder = ({factions}) => {
    return (
        <svg width="600px" height="100px" viewBox="2.5 0 1 1">
            {factions.map((factionInfo, i)=> {
                let opacity = factionInfo.label === "pass" ? 0.2 : 1.0;
                let circle = <g/>
                if (factionInfo.active) {
                    circle = <circle cx={i+0.5} cy={0.5} r={0.48} style={{
                        fillOpacity: 0.,
                        strokeWidth: 0.04,
                        stroke:"white"
                    }} />;
                }
                return (
                    <g key={i}>
                        <Logo x={i} y={0} faction={factionInfo.faction} diameter={1} style={{
                            opacity: opacity
                        }} />
                        {circle}
                        <text x={i+.5} y={0.6} textAnchor="middle" style={{
                            fill: "white",
                            stroke: "black",
                            strokeWidth: 0.02,
                            font: `bold 0.35px sans-serif`}}>{factionInfo.label}</text>
                    </g>
                );
            })}
        </svg>
    );
}

class Bidding extends React.Component {
    getCards () {
        let cards = [];
        let reverses = this.props.roundstate.up_for_auction.length;
        if (this.props.roundstate.up_for_auction.next !== undefined){
            cards.push(<TreacheryCard
                key="next" name={this.props.roundstate.up_for_auction.next}/>);
            reverses -=1;
        }
        for (let i=0; i<reverses;i++){
            cards.push(<TreacheryCard key={i} name="Reverse"/>);
        }
        return cards;
    }
    getBids () {
        return Object.keys(this.props.roundstate.stage_state.bids).map((faction) => {
            return (
                <li key={faction}>
                    {faction} : {this.props.roundstate.stage_state.bids[faction]}
                </li>
            );
        });
    }
    render () {
        let {roundstate, logoPositions, stormSector} = this.props;
        const factionOrder = getFactionOrder(roundstate, logoPositions, stormSector);
        let turnOrder = <FactionOrder factions={factionOrder.map((faction)=>{
            return {
                faction: faction,
                label: this.props.roundstate.stage_state.bids[faction],
                active: faction === this.props.roundstate.stage_state.substage_state.faction_turn
            };
        })} />;
        if (roundstate.stage_state.stage === "auction"){
            return (
                <div style={{display:"flex", flexDirection:"column"}}>
                    <h4>Bidding Round</h4>
                    {turnOrder}
                    <div>
                        {this.getCards()}
                    </div>
                </div>
            );
        }
        return <div/>;
    }
}

module.exports = Bidding;