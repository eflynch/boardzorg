import React, {useState} from 'react';

import {randInt} from '../utils';


export default function Card({type, name, selected, onClick, width, children, peak}) {

    const [examine, setExamine] = useState(false);

    if (width === undefined) {
        width = 125;
    }
    if (name === "Cheap-Hero/Heroine"){
        name = ["Cheap-Hero", "Cheap-Heroine"][randInt(0,1)];
    }
    let examineStyle = {
        zIndex: 1000,
        position: "fixed",
        top: 0,
        left: 0
    };

    return (
        <div style={examine ? examineStyle : {position:"relative"}} >
            <img
                src={`/static/app/png/${type}-${name.replace(" ", "-")}.png`}
                className={"card" + (selected ? " selected" : "") + (onClick ? " active" : "") + (peak ? " peak": "")}
                onClick={(e)=>{
                    if (examine) {
                        setExamine(false);
                        return;
                    }
                    if (e.shiftKey){
                        setExamine(true);
                        return;
                    }
                    if (onClick !== undefined) {
                        onClick(e);
                    }
                }}
                width={examine ? 400 : width} />
            {children}
        </div>
        );
};
