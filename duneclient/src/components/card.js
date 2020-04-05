import React from 'react';

import {randInt} from '../utils';


export default function Card({type, name, width}) {
    if (width === undefined) {
        width = 125;
    }
    if (name === "Cheap-Hero/Heroine"){
        name = ["Cheap-Hero", "Cheap-Heroine"][randInt(0,1)];
    } 
    return <img
        src={`/static/app/png/${type}-${name.replace(" ", "-")}.png`}
        width={width} />;
};
