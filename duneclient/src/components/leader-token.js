import React from 'react';

export default function LeaderToken({traitor, dead, onClick, selected, name}) {
    const src = name == "Kwisatz-Haderach" ? "/static/app/png/Token-Kwisatz-Haderach.png" : `/static/app/png/Leader-${name}.png`;
    return <img className={"leader-token" +
                           (traitor ? " traitor": "") +
                           (dead ?  " dead" : " alive") +
                           (onClick ? " active" : "") +
                           (selected ? " selected" : "")}
                src={src}
                onClick={onClick}
                width={75} />;
};
