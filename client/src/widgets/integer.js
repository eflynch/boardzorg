import React from 'react';
import Slider, { Range } from 'rc-slider';

export default function Integer({args, setArgs, type, min, max}) {
    return (
        <div>
            {args} {type ? type : ""}
            <Slider min={min} max={max} step={1} value={parseInt(args)}
                onChange={(value)=>{
                    setArgs(value.toString());
            }} />
        </div>
    );
};
