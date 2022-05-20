import React from 'react';

const Logo = ({faction, diameter, ...props}) => {
    return <img {...props} src={`/static/app/png/${faction}_logo.png`} width={diameter} height={diameter}/>;
};

const PASS_LABELS = ["pass", "done", "moved"];

export default function FactionOrder({factions, diameter, margin}) {
    if (diameter === undefined) {
        diameter = 80;
    }
    if (margin === undefined) {
        margin = 3;
    }
    return (
        <div style={{display:"flex"}}>
            {factions.map((factionInfo, i)=> {
                const passed = PASS_LABELS.indexOf(factionInfo.label) !== -1;
                const opacity = passed ? 0.2 : 1.0;
                let circle = <div/>
                const d = factionInfo.active ? diameter * 1.2 : diameter;
                if (factionInfo.active) {
                    circle = <div style={{
                        position:"absolute",
                        top:0,
                        left:0,
                        width:d,
                        height:d,
                        borderRadius: d / 2,
                        backgroundColor: "white",
                    }} />;
                }
                return (
                    <div key={i} style={{position:"relative", width:d, height:d}}>
                        {circle}
                        <Logo faction={factionInfo.faction} diameter={d - margin * 2} style={{
                            position:"absolute",
                            top: 0,
                            left: 0,
                            margin: margin,
                            opacity: opacity,
                        }} />
                        <div style={{position:"absolute", top:0, left: 0, width: d, height: d, display:"flex", justifyContent:"center", alignItems:"center"}}>
                            <span style={{
                                WebkitTextStrokeWidth: 1,
                                WebkitTextStrokeColor: "black",
                                color:"white",
                                fontSize: d * 0.35,
                                fontWeight: "bold"}}>
                                    {factionInfo.label}
                            </span>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
