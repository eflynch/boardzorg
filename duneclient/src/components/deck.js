import React from 'react';

import Card from './card';


export default function Deck({facedown, faceup, type}) {
    const Faceup = (faceup) => {
        return faceup.concat().reverse().map((name, i )=> {
            return (
                <div key={name} style={{position: "absolute", top:0, left: 0}}>
                    <Card type={type} name={name} width={100}/>
                </div>
            );
        });
    };

    const Facedown = (facedown) => {
        let cards = [
            <Card type={type} name="Reverse" width={100}>
                <div style={{position: "absolute", color:"white", top:4, right: 4, fontSize: 10}}>{facedown.length} Remain</div>
            </Card>
        ];
        if (facedown.next) {
            cards.push(<Card type={type} name={facedown.next} width={100} peak={true} />);
        }
        return cards.map((card, i) => {
            return (
                <div key={i} style={{position: "absolute", top:0, left: 0}}>
                    {card}
                </div>
            );
        });
    };
    return (
        <div style={{display:"flex",flexDirection: "column"}}>
            <div style={{position: "relative"}}>
                <div className="question-card">Empty</div>
                {Facedown(facedown)}
            </div>
            <div style={{position: "relative"}}>
                <div className="question-card">Empty</div>
                {Faceup(faceup)}
            </div>
        </div>
    );
};
