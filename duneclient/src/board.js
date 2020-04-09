import React from 'react';
import ReactDOM from 'react-dom';
import update from 'immutability-helper';

import {SpiceLocations, TokenLocations, LogoLocations} from './board-data';

import Spice from './components/spice';
import TokenPile from './components/token-pile';
import {spacePaths, spaceSectorPaths, sectorPaths} from './paths';

const TRANSFORM=`translate(0.000000,1.000000) scale(${0.100000/848},${-0.100000/848})`;


const Logo = ({faction, diameter, x, y}) => {
    return <image xlinkHref={`/static/app/png/${faction}_logo.png`} x={x} y={y} width={diameter} height={diameter}/>;
}

const BlankLogo = ({diameter, x, y, ...props}) => {
    return <circle className="blank-logo" r={diameter/2} cx={x+diameter/2} cy={y+diameter/2} {...props}/>;
}

const MapPart = ({className, selected, onClick, paths, ...props}) => {
    return (
        <g {...props} className={className + (selected ? " selected" : "") + (onClick? " active" : "")}
            onClick={()=>{
                if (onClick) {
                    onClick(territory);
                }
            }}
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
        paths={sectorPaths[sector]}
    />
};


class Board extends React.Component {
    constructor(props) {
      super(props);
      this.state = { size: '0' };
      this.updateWindowDimensions = this.updateWindowDimensions.bind(this);
    }

    componentDidMount() {
      this.updateWindowDimensions();
      window.addEventListener('resize', this.updateWindowDimensions);
    }

    componentWillUnmount() {
      window.removeEventListener('resize', this.updateWindowDimensions);
    }

    updateWindowDimensions() {
      this.setState({size: Math.min(window.innerWidth - 100, 800)});
    }

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
                <Spice key={space.name+"spice"} x={left} y={top} amount={space.spice} width={0.08} height={0.08}/>
            );
        }
        return spice;
    }

    getLogos () {
        const {me, interaction, setInteraction} = this.props;
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

        const mode = interaction.mode;
        if (mode === "token-select" || interaction["token-select"]) {
            logos = logos.concat(emptyPositions.map((position)=>{
                const {top, left} = LogoLocations[position];
                const onClick = mode === "token-select" ? () => {
                    setInteraction(update(interaction, {
                        [mode]: {$set: position},
                        mode: {$set: null},
                    }));
                } : null;
                if (interaction["token-select"] === null) {
                    return <BlankLogo
                            key={position}
                            diameter={0.05}
                            x={left} y={top}
                            onClick={onClick}
                            className={onClick ? "active" : ""}/>;
                } else if (interaction["token-select"] === position) {
                    return <Logo key={"me"} diameter={0.05} faction={me} x={left} y={top}/>;
                }
            }));
        }
        return logos;
    }

    _getMapParts(paths, className, onClick, selected) {
        let spaces = Object.keys(paths).map((territory) => {
            const isSelected = (selected !== undefined && selected !== null) && (territory == selected.replace(" ", "-"));
            return <MapPart key={territory +"path"} className={className} onClick={()=>{onClick(territory);}} selected={isSelected} paths={paths[territory]} />;
        });
        return spaces;
    }

    getSpaces () {
        const {interaction, setInteraction} = this.props;
        const inInteraction = interaction.mode === "space-select";
        const selected = interaction["space-select"];

        if (!inInteraction && !selected) {
            return <g/>;
        }

        const onClick = inInteraction ? (space) => {
            setInteraction(update(interaction, {[interaction.mode]: {$set: space}, mode: {$set: null}}));
        } : null;

        return this._getMapParts(spacePaths, "space", onClick, selected);
    }

    getSpaceSectors () {
        const {interaction, setInteraction} = this.props;

        const inInteraction =
              interaction.mode === "space-sector-select-start" ||
              interaction.mode === "space-sector-select-end";

        const selected =
              interaction["space-sector-select-end"] || interaction["space-sector-select-start"];
        if (!inInteraction && !selected) {
            return <g/>;
        }

        const onClick = inInteraction ? (spaceSector) => {
            let split = spaceSector.split("-");
            const sector = split.pop();
            const space = split.join("-");
            setInteraction(update(interaction, {
                [interaction.mode]: {$set: [space, sector].join(" ")},
                mode: {$set: null}}));
        } : null;

        return  this._getMapParts(spaceSectorPaths, "spaceSector", onClick, selected);
    }

    getSectors () {
        const {interaction, setInteraction} = this.props;
        const inInteraction = interaction.mode === "sector-select";
        const selected = interaction["sector-select"];

        if (!inInteraction && !selected) {
            return <g/>;
        }

        const onClick = inInteraction ? (space) => {
            setInteraction(update(interaction, {[interaction.mode]: {$set: sector}, mode: {$set: null}}));
        } : null;

        return this._getMapParts(sectorPaths, "sector", onClick, selected);
    }

    render () {
        let {round_state, turn, map_state} = this.props.state;
        let AllSpaces = Object.keys(spaceSectorPaths);
        let transform=`translate(0.000000,1.000000) scale(${0.100000/848},${-0.100000/848})`;
        let spaces = AllSpaces.map((territory) => {
                return <g className="space"
                    onClick={()=>{}}
                    key={territory +"path"} transform={transform}>
                    {spaceSectorPaths[territory].map((p, i)=><path key={i} d={p}/>)}
                }}
                </g>
            });

        let futureStorm = <g/>;
        if (this.props.futureStorm !== undefined) {
            futureStorm = <Storm sector={this.props.futureStorm} color="rgba(0, 0, 255, 0.2)"/>;
        }
        let futureSpice = <g/>;
        if (this.props.futureSpice !== undefined) {
            const spiceSector = map_state.filter((s)=>s.name === this.props.futureSpice)[0].spice_sector;
            futureSpice = <MapPart style={{
                fill: "green",
                opacity: 0.4
            }} paths={spaceSectorPaths[[this.props.futureSpice, spiceSector].join("-")]}/>;
        }
        return (
            <div className="board">
                <svg width={this.state.size} height={this.state.size} viewBox={`0 0 1 1`}>
                    <text x={0.04} y={0.04} style={{fill: "white", font: "normal 0.02px Optima"}}>Turn {turn} / 10</text>
                    <image xlinkHref="/static/app/png/board.png" x="0" y="0" width="1" height="1"/>
                    {futureStorm}
                    {futureSpice}
                    {this.getSpaces()}
                    {this.getSpaceSectors()}
                    {this.getLogos()}
                    {this.getSpice()}
                    {this.getTokenPiles()}
                    <Storm sector={this.props.stormSector} color="rgba(255, 0, 0, 0.5)"/>
                </svg>
            </div>
        );
    }
}


module.exports = Board;
