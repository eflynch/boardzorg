import React, {useState} from 'react';
import Slider, { Range } from 'rc-slider';


export default function Units({args, setArgs, fedaykin, sardaukar, maxOnes}) {
    const units = args.split(",").map((i)=>parseInt(i));
    const numOnes = units.filter((i)=>i===1).length;
    console.log(numOnes);
    const numTwos = units.filter((i)=>i===2).length;

    let bonus = <div/>;
    if (fedaykin || sardaukar) {
        bonus = (
            <div style={{display: "flex"}}>
                <div className="label">{fedaykin ? "Fedaykin: " : "Sardaukar: "}{numTwos}</div>
                <Slider min={0} max={fedaykin ? 3 : 5} step={1} dots={true} value={numTwos}
                    onChange={(value)=>{
                        const ones = Array(numOnes).fill("1").join(",");
                        const twos = Array(value).fill("2").join(",");
                        if (ones && twos){
                            setArgs([ones, twos].join(","));
                        } else {
                            setArgs(ones + twos);
                        }
                    }} />
            </div>
        );
    }
    return (
        <div className="unit-select">
            <div style={{display: "flex"}}>
                <div className="label">Units: {numOnes}</div>
                <Slider min={0} max={maxOnes || 20} step={1} dots={true} value={numOnes}
                    onChange={(value)=>{
                        const ones = Array(value).fill("1").join(",");
                        const twos = Array(numTwos).fill("2").join(",");
                        if (ones && twos){
                            setArgs([ones, twos].join(","));
                        } else {
                            setArgs(ones + twos);
                        }
                    }} />
            </div>
            {bonus} 
        </div>
    );
};