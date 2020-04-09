import React from 'react';

const textHeight = 0.35;

const Spice = ({amount, width, ...props}) => {
    return (
        <svg className="spice-pile" width={width} viewBox="0 0 1 1" {...props}>
            <image xlinkHref={`/static/app/png/melange_${Math.ceil(amount/3)}.png`} x="0" y="0" width="1" height="1"/>
            <text x={0.5} y={0.75} style={{
                fill: "yellow",
                stroke:"black",
                strokeWidth:textHeight * 0.06,
                font: `bolder ${textHeight}px impact`
            }}>{amount}</text>
        </svg>
    );
}

module.exports = Spice;
