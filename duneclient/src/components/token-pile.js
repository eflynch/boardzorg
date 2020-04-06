import React from 'react';

const Token = ({faction, coexist, ...props}) => {
    return <image xlinkHref={`/static/app/png/${faction}${faction==="bene-gesserit" && coexist ? "_coexist" : ""}_token.png`} {...props}/>
}


const tokenAspect = 76/142;
const tokenHeight = 0.1; 
const textHeight = 0.3;

const TokenPile = ({width, faction, coexist, number, bonus, x, y}) => {
    const unitHeight = (tokenAspect + number * tokenHeight + textHeight);

    x = x === undefined ? "0" : x - width/2;
    y = y === undefined ? "0" : y - (width * (unitHeight - tokenAspect/2));

    let tokens = [];
    for (let i=0; i < number; i++){
        tokens.push(<Token key={i} faction={faction} coexist={coexist} width={1} height={tokenAspect} x={0} y={(unitHeight - tokenAspect - textHeight) * (1-(i/number)) + textHeight}/>);
    }
    return (
        <svg className={"token-pile"} x={x} y={y} width={width} height={unitHeight * width} viewBox={`0 0 1 ${unitHeight}`}>
            {tokens}
            <text x={0.53} y={textHeight + 0.01} textAnchor="middle" style={{
                fill: "yellow",
                font: `bold ${textHeight}px sans-serif`
            }}>{"" + number + (bonus ? ` (+${bonus})` : "")}</text>
            <text x={0.5} y={textHeight} textAnchor="middle" style={{
                fill: "black",
                font: `bold ${textHeight}px sans-serif`
            }}>{"" + number + (bonus ? ` (+${bonus})` : "")}</text>
        </svg>
    );
};

module.exports = TokenPile;
