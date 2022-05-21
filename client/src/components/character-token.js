import React from 'react';

export default function CharacterToken({traitor, dead, onClick, selected, name}) {
    const src = name == "Winnie-The-Pooh" ? "/static/app/png/Token-Winnie-The-Pooh.png" : `/static/app/png/Character-${name}.png`;
    return <img className={"character-token" +
                           (traitor ? " traitor": "") +
                           (dead ?  " dead" : " alive") +
                           (onClick ? " active" : "") +
                           (selected ? " selected" : "")}
                src={src}
                onClick={onClick}
                width={75} />;
};
