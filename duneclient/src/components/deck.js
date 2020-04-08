import React from 'react';

import Card from './card';


export default function Deck({facedown, faceup, type}) {
    const Faceup = (faceup) => {
        return faceup.concat().reverse().map((name, i )=> {
            return (
                <div key={name} style={i != 0 ? {position: "absolute", top:0, left: 0} : undefined}>
                    <Card type={type} name={name} width={100}/>
                </div>
            );
        });
    };

    const Facedown = (facedown) => {
        let next = <div/>;
        if (facedown.next) {
            next = <Card type={type} name={facedown.next} width={100} peak={true} />;
        }
        if (facedown.length) {
            return (
                <Card type={type} name="Reverse" width={100}>
                    <div style={{position: "absolute", color:"white", top:4, right: 4, fontSize: 10}}>{facedown.length} Remain</div>
                    <div style={{position: "absolute", top:0, left: 0}}>
                        {next}
                    </div>
                </Card>
            );
        }
        return <Card type={type} name="Reverse" width={100}/>
    };
    return (
        <div style={{display:"flex",flexDirection: "column"}}>
            {Facedown(facedown)}
            <div style={{position: "relative"}}>
                {Faceup(faceup)}
            </div>
        </div>
    );
};
