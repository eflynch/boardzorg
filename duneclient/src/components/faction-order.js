import React from 'react';

const Logo = ({faction, diameter, x, y, ...props}) => {
    return <image {...props} xlinkHref={`/static/app/png/${faction}_logo.png`} x={x} y={y} width={diameter} height={diameter}/>;
};

const PASS_LABELS = ["pass", "done", "moved"];

export default function FactionOrder({factions}) {
    return (
        <svg width="480px" height="80px" viewBox="2.5 0 1 1">
            {factions.map((factionInfo, i)=> {
                const passed = PASS_LABELS.indexOf(factionInfo.label) !== -1;
                const opacity = passed ? 0.2 : 1.0;
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
