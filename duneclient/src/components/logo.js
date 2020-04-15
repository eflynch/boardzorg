import React, {useState} from 'react';


export default function Logo({faction, diameter, ...props}){
   return <img {...props} src={`/static/app/png/${faction}_logo.png`} width={diameter} height={diameter}/>;
};
