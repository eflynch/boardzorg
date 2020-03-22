import React from 'react';

const Spice = ({amount, width, ...props}) => {
    return (
        <svg width={width} viewBox="0 0 1 1" {...props}>
            <image xlinkHref={`/static/app/png/melange_${Math.ceil(amount/3)}.png`} x="0" y="0" width="1" height="1"/>
            <text x={0.5} y={0.75} style={{
                fill: "black",
                font: "bold 0.35px sans-serif"
            }}>{amount}</text>
            <text x={0.51} y={0.74} style={{
                fill: "yellow",
                font: "bold 0.35px sans-serif"
            }}>{amount}</text>
        </svg>
    );
}

module.exports = Spice;
