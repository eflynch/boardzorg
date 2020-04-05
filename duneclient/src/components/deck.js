import React from 'react';

import Card from './card';


export default function Deck({facedown, faceup, type}) {
    const Faceup = (faceup) => {
        if (faceup.length) {
            return <Card type={type} name={faceup[0]} width={100}/>;
        }
    };
    return (
        <div style={{display:"flex",flexDirection: "column"}}>
            <Card type={type} name="Reverse" width={100}/>
            {Faceup(faceup)}
        </div>
    );
};
