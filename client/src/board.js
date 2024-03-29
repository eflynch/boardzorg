import React from 'react';

import {SpiceLocations, TokenLocations, LogoLocations, TRANSFORM, Paths} from './board-data';

import Spice from './components/spice';
import TokenPile from './components/token-pile';


const Logo = ({faction, diameter, x, y}) => {
    return <image xlinkHref={`/static/app/png/${faction}_logo.png`} x={x} y={y} width={diameter} height={diameter}/>;
}

const Alliance = ({factions, diameter, overlap, cx, cy}) => {
    const width = (diameter - overlap) * factions.length;
    return (
        <g>
            {factions.map((faction, i)=>{
                return <Logo key={faction} faction={faction} diameter={diameter}
                             x={(cx - width/2) + i * (diameter - overlap)}
                             y={cy - diameter/2} />;
            })}
        </g>
    );
}

const BlankLogo = ({diameter, className, x, y, ...props}) => {
    return <circle className={"blank-logo " + className} r={diameter/2} cx={x+diameter/2} cy={y+diameter/2} {...props}/>;
}

const MapPart = ({className, selected, onClick, paths, ...props}) => {
    return (
        <g {...props} className={className + (selected ? " selected" : "") + (onClick? " active" : "")}
            onClick={onClick ? onClick : undefined}
            pointerEvents={onClick ? undefined : "none"}
            transform={TRANSFORM}>
            {paths.map((p, i)=><path key={i} d={p}/>)}
        }}
        </g>
    );
}

const Storm = ({sector, color}) => {
    return <MapPart className="storm"
        style={{
            fill: color
        }}
        paths={Paths.sectors[sector]}
    />
};


class Board extends React.Component {
    getTokenPiles () {
        let {map_state} = this.props.state;
        let tokens = [];
        let orders = {};
        for (let i=0; i < map_state.length; i++){
            let space = map_state[i];
            if (space.forces === null){
                continue;
            }
            for (var faction in space.forces){
                if (!space.forces.hasOwnProperty(faction)){
                    continue;
                }
                for (var sector in space.forces[faction]){
                    if (!space.forces[faction].hasOwnProperty(sector)){
                        continue;
                    }
                    if (orders.hasOwnProperty(space.name)){
                        orders[space.name] += 1;
                    } else {
                        orders[space.name] = 1;
                    }
                    let number = space.forces[faction][sector].length;
                    let power = space.forces[faction][sector].reduce((a, b) => a + b, 0);
                    if (TokenLocations[space.name] === undefined) {
                        console.warn(`Missing board-data for ${space.name} all sectors including ${sector}`);
                        continue;
                    }

                    if (TokenLocations[space.name][sector] === undefined) {
                        console.warn(`Missing board-data for ${space.name} :: ${sector}`);
                        continue;
                    }

                    if (TokenLocations[space.name][sector][orders[space.name]] === undefined) {
                        console.warn(`Missing board-data for ${space.name} :: ${sector} # ${orders[space.name]}`);
                        continue;
                    }

                    let {left, top} = TokenLocations[space.name][sector][orders[space.name]];
                    tokens.push(
                        [
                            top, 
                            <TokenPile key={i + faction + sector} x={left} y={top}
                                       number={number}
                                       bonus={number !== power ? power - number : null}
                                       width={0.05}
                                       coexist={space.coexist}
                                       faction={faction}/>
                        ]
                    );
                }
            }
        }
        tokens.sort((a, b) => {return a[0] - b[0]});
        return tokens.map(([top, pile])=>pile);
    }

    getSpice () {
        let {map_state} = this.props.state;
        let spice = [];
        for (let i=0; i < map_state.length; i++){
            let space = map_state[i];
            if (!space.spice){
                continue;
            }
            const {left, top} = SpiceLocations[space.name];
            spice.push(
                <Spice key={space.name+"spice"} x={left - 0.04} y={top - 0.04} amount={space.spice} width={0.08} height={0.08}/>
            );
        }
        return spice;
    }

    getLogos () {
        const {me, interaction, selection} = this.props;
        const allLogoPositions = Object.keys(LogoLocations).map((i)=>parseInt(i));
        const emptyPositions = allLogoPositions.filter((position)=>{
            const matches = this.props.logoPositions.filter(([faction, pos]) => {
                return (pos !== null) && (pos === position);
            });
            return matches.length === 0;
        });
        let logos = this.props.logoPositions
            .filter(([faction, position])=> {return position !== null;})
            .map(([faction, position]) => {
                const {top, left} = LogoLocations[position];
                return <Logo key={faction} diameter={0.05} faction={faction} x={left} y={top}/>;
            });

        if (interaction.mode === "token-select" || selection["token-select"]) {
            logos = logos.concat(emptyPositions.map((position)=>{
                const {top, left} = LogoLocations[position];
                const onClick = interaction.mode === "token-select" ? () => {
                    interaction.action(position);
                } : null;
                if (selection["token-select"] == null) {
                    return <BlankLogo
                            key={position}
                            diameter={0.05}
                            x={left} y={top}
                            onClick={onClick}
                            className={onClick ? "active" : ""}/>;
                } else if (selection["token-select"] === position) {
                    return <Logo key={"me"} diameter={0.05} faction={me} x={left} y={top}/>;
                }
            }));
        }
        return logos;
    }

    _getMapParts(paths, className, onClick, selectedParts) {
        let spaces = Object.keys(paths).map((territory) => {
            let thisOnClick = onClick ? ()=>{onClick(territory);} : undefined;
            const isSelected = selectedParts.indexOf(territory) !== -1;
            return <MapPart key={territory +"path"} className={className} onClick={thisOnClick} selected={isSelected} paths={paths[territory]} />;
        });
        return spaces;
    }

    getSpaces () {
        const {interaction, selection} = this.props;
        const inInteraction = interaction.mode === "space-select";
        const selectedParts = [selection["space-select"]];

        if (!inInteraction && !selectedParts.length) {
            return <g/>;
        }

        const onClick = inInteraction ? (space) => {
            interaction.action(space);
        } : null;

        return this._getMapParts(Paths.spaces, "space", onClick, selectedParts);
    }

    getSpaceSectors () {
        const {interaction, selection} = this.props;

        const inInteraction =
              interaction.mode === "space-sector-select-start" ||
              interaction.mode === "space-sector-select-end";

        const selectedParts = [selection["space-sector-select-end"], selection["space-sector-select-start"]].map((part)=>{
            return part !== undefined ? part.replace(" ", "-") : part;
        }).filter((x) => x);
        if (!inInteraction && !selectedParts.length) {
            return <g/>;
        }
        const onClick = inInteraction ? (spaceSector) => {
            let split = spaceSector.split("-");
            const sector = split.pop();
            const space = split.join("-");
            interaction.action(`${space} ${sector !== "" ? sector : -1}`);
        } : null;

        return  this._getMapParts(Paths.spaceSectors, "spaceSector", onClick, selectedParts);
    }

    getMovementArrows () {
        const {interaction, selection} = this.props;
        if (selection["space-sector-select-start"] === undefined || selection["space-sector-select-end"] === undefined) {
            return;
        }
        const [aSpace, aSector] = selection["space-sector-select-start"].split(" ");
        const [bSpace, bSector] = selection["space-sector-select-end"].split(" ");
        return (
            <line stroke="black" strokeWidth={0.005}
                x1={TokenLocations[aSpace][aSector][1].left} y1={TokenLocations[aSpace][aSector][1].top}
                x2={TokenLocations[bSpace][bSector][1].left} y2={TokenLocations[bSpace][bSector][1].top} />
        );
    }

    getSectors () {
        const {interaction, selection} = this.props;
        const inInteraction = interaction.mode === "sector-select";
        const selectedParts = [selection["sector-select"]];

        if (!inInteraction && !selectedParts.length) {
            return <g/>;
        }

        const onClick = inInteraction ? (space) => {
            interaction.action(space);
        } : null;

        return this._getMapParts(Paths.sectors, "sector", onClick, selectedParts);
    }

    getShaiHulud () {
        let {shai_hulud, map_state} = this.props.state;
        if (shai_hulud) {
            const space = map_state.filter((s)=>s.name === shai_hulud)[0];
            let wormLocation = TokenLocations[shai_hulud][space.sectors[0]][3];
            if (space.spice_sector != undefined) {
                wormLocation = SpiceLocations[shai_hulud];
            }
            return (
                <image className={"shai-hulud"} xlinkHref={`/static/app/png/shai-hulud.png`} x={wormLocation.left - 0.09} y={wormLocation.top - 0.12} width={0.2} height={0.2}/>
            );
        }
    }

    getAtomics() {
        let {shield_wall} = this.props.state;
        if (!shield_wall) {
            return (
                <image xlinkHref={`/static/app/png/atomics.png`} x={0.5} y={0.24} width={0.2} height={0.2} style={{opacity:0.8}}/>
            );
        }
    }

    render () {
        let {round_state, turn, map_state, alliances} = this.props.state;
        let AllSpaces = Object.keys(Paths.spaceSectors);
        let spaces = AllSpaces.map((territory) => {
                return <g className="space"
                    onClick={()=>{}}
                    key={territory +"path"} transform={TRANSFORM}>
                    {Paths.spaceSectors[territory].map((p, i)=><path key={i} d={p}/>)}
                }}
                </g>
            });

        let futureStorm = <g/>;
        if (this.props.futureStorm !== undefined) {
            futureStorm = <Storm sector={this.props.futureStorm} color="rgba(0, 0, 255, 0.2)"/>;
        }
        let futureSpice = <g/>;
        if (this.props.futureSpice !== undefined && this.props.futureSpice !== "Shai-Hulud") {
            const spiceSector = map_state.filter((s)=>s.name === this.props.futureSpice)[0].spice_sector;
            futureSpice = <MapPart style={{
                fill: "green",
                opacity: 0.4
            }} paths={Paths.spaceSectors[[this.props.futureSpice, spiceSector].join("-")]}/>;
        }
        return (
            <div className="board">
                <svg width={"100%"} viewBox={`0 0 1 1`}>
                    <text x={0.11} y={0.11} style={{fill: "white", font: "normal 0.1px Optima"}}>{turn}</text>
                    <image xlinkHref="/static/app/png/board.png" x="0" y="0" width="1" height="1"/>
                    {alliances.filter(alliance=>alliance.length > 1).map((alliance, i)=> {
                        return <Alliance factions={alliance} key={alliance.join("-")} diameter={0.04} overlap={0.004} cx={0.08} cy={0.08 + 0.05 * i}/>;
                    })}
                    {futureStorm}
                    {futureSpice}
                    {this.getSpaces()}
                    {this.getSpaceSectors()}
                    <Storm sector={this.props.stormSector} color="rgba(255, 0, 0, 0.5)"/>
                    {this.getMovementArrows()}
                    {this.getLogos()}
                    {this.getSpice()}
                    {this.getTokenPiles()}
                    {this.getShaiHulud()}
                    {this.getAtomics()}
                </svg>
            </div>
        );
    }
}


module.exports = Board;
