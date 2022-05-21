import React, {useState} from 'react';
import Slider, { Range } from 'rc-slider';


export default function Minions({args, setArgs, woozles, very_sad_boys, maxOnes}) {
    const minions = args.split(",").map((i)=>parseInt(i));
    const numOnes = minions.filter((i)=>i===1).length;
    const numTwos = minions.filter((i)=>i===2).length;

    let bonus = <div/>;
    if (woozles || very_sad_boys) {
        let onChange = undefined;
        if (setArgs !== undefined) {
            onChange = (value)=>{
                const ones = Array(numOnes).fill("1").join(",");
                const twos = Array(value).fill("2").join(",");
                if (ones && twos){
                    setArgs([ones, twos].join(","));
                } else {
                    setArgs(ones + twos);
                }
            };
        }
        bonus = (
            <div style={{display: "flex"}}>
                <div className="label">{woozles ? "Woozles: " : "VerySadBoys: "}{numTwos}</div>
                <Slider min={0} max={woozles ? 3 : 5} step={1} dots={true} value={numTwos}
                    onChange={onChange} />
            </div>
        );
    }

    let onChange = undefined;
    if (setArgs !== undefined) {
        onChange = (value)=>{
            const ones = Array(value).fill("1").join(",");
            const twos = Array(numTwos).fill("2").join(",");
            if (ones && twos){
                setArgs([ones, twos].join(","));
            } else {
                setArgs(ones + twos);
            }
        };
    }

    return (
        <div className="minion-select">
            <div style={{display: "flex"}}>
                <div className="label">Minions: {numOnes}</div>
                <Slider min={0} max={maxOnes || 20} step={1} dots={true} value={numOnes}
                    onChange={onChange} />
            </div>
            {bonus} 
        </div>
    );
};
