import React from 'react';

const Token = ({faction, chill_out, ...props}) => {
    return <image xlinkHref={`/static/app/png/${faction}${faction==="rabbit" && chill_out ? "_chill_out" : ""}_token.png`} {...props}/>
}


const tokenAspect = 76/142;
const tokenHeight = 0.1; 
const textHeight = 0.5;

const TokenPile = ({width, faction, chill_out, number, bonus, x, y}) => {
    const minionHeight = (tokenAspect + number * tokenHeight + textHeight);

    x = x === undefined ? "0" : x - width/2;
    y = y === undefined ? "0" : y - (width * (minionHeight - tokenAspect/2));

    let tokens = [];
    for (let i=0; i < number; i++){
        tokens.push(<Token key={i} faction={faction} chill_out={chill_out} width={1} height={tokenAspect} x={0} y={(minionHeight - tokenAspect - textHeight) * (1-(i/number)) + textHeight}/>);
    }
    const text = `${number}${bonus ? `+${bonus}` : ""}`;
    return (
        <svg className={"token-pile"} x={x} y={y} width={width} height={minionHeight * width} viewBox={`0 0 1 ${minionHeight}`}>
            {tokens}
            <text x={0.5} y={textHeight} textAnchor="middle" style={{
                fill: "white",
                stroke:"black",
                strokeWidth:textHeight * 0.06,
                font: `bolder ${textHeight}px impact`
            }}>{text}</text>
        </svg>
    );
};

module.exports = TokenPile;
