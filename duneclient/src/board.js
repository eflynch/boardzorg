import React from 'react';
import ReactDOM from 'react-dom';
import update from 'immutability-helper';

import {SpiceLocations, TokenLocations, LogoLocations} from './board-data';

import Spice from './components/spice';
import TokenPile from './components/token-pile';
import {spacePaths, spaceSectorPaths, sectorPaths} from './paths';


const Storm = ({sector}) => {
    let transform=`translate(0.000000,1.000000) scale(${0.100000/848},${-0.100000/848})`;
    return <g className="storm"
        onClick={()=>{
            onClick(territory);
        }}
        transform={transform}>
            {sectorPaths[sector].map((p, i)=><path key={i} d={p}/>)}
        }}
    </g>
};

const Logo = ({faction, diameter, x, y}) => {
    return <image xlinkHref={`/static/app/png/${faction}_logo.png`} x={x} y={y} width={diameter} height={diameter}/>;
}

const BlankLogo = ({diameter, x, y, ...props}) => {
    return <circle className="blank-logo" r={diameter/2} cx={x+diameter/2} cy={y+diameter/2} {...props}/>;
}


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
        let tokens = [];
        let orders = {};
        for (let i=0; i < this.props.boardstate.length; i++){
            let space = this.props.boardstate[i];
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
                    let {left, top} = TokenLocations[space.name][sector][orders[space.name]];
                    tokens.push(
                        <TokenPile key={i + faction + sector} x={left} y={top}
                                   number={number}
                                   bonus={number !== power ? power - number : null}
                                   width={0.05}
                                   coexist={space.coexist}
                                   faction={faction}/>
                    );
                }
            }
        }
        return tokens;
    }

    getSpice () {
        let spice = [];
        for (let i=0; i < this.props.boardstate.length; i++){
            let space = this.props.boardstate[i];
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

        if (interaction.mode === "token-select") {
            logos = logos.concat(emptyPositions.map((position)=>{
                const {top, left} = LogoLocations[position];
                if (interaction.selected === null) {
                    return <BlankLogo key={position} diameter={0.05} x={left} y={top} onClick={(e)=>{
                        setInteraction(update(interaction, {selected: {$set: position}}));
                    }}/>;
                } else if (interaction.selected === position) {
                    return <Logo key={"me"} diameter={0.05} faction={me} x={left} y={top}/>;
                }
            }));
        }
        return logos;
    }

    _getMapParts(paths, className, onClick, selected) {
        let transform=`translate(0.000000,1.000000) scale(${0.100000/848},${-0.100000/848})`;
        let spaces = Object.keys(paths).map((territory) => {
            const isSelected = (selected !== undefined && selected !== null) && (territory == selected.replace(" ", "-"));
            return <g className={className + (isSelected ? " selected": "")}
                onClick={()=>{
                    onClick(territory);
                }}
                key={territory +"path"} transform={transform}>
                {paths[territory].map((p, i)=><path key={i} d={p}/>)}
            }}
            </g>
        });
        return spaces;
    }

    getSpaces () {
        const {interaction, setInteraction} = this.props;
        if (interaction.mode !== "space-select") {
            return <g/>;
        }
        return this._getMapParts(spacePaths, "space", (space)=>{
            setInteraction(update(interaction, {selected: {$set: space}}));
        }, interaction.selected);
    }

    getSpaceSectors () {
        const {interaction, setInteraction} = this.props;
        if (interaction.mode !== "space-sector-select") {
            return <g/>;
        }
        return  this._getMapParts(spaceSectorPaths, "spaceSector", (spaceSector)=>{
            let split = spaceSector.split("-")
            const sector = split.pop()
            const space = split.join("-")
            setInteraction(update(interaction, {selected: {$set: [space, sector].join(" ")}}));
        }, interaction.selected);
    }

    getSectors () {
        const {interaction, setInteraction} = this.props;
        if (interaction.mode !== "sector-select") {
            return <g/>;
        }
        return this._getMapParts(sectorPaths, "sector", (sector)=>{
            setInteraction(update(interaction, {selected: {$set: sector}}));
        }, interaction.selected);
    }

    render () {

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
        return (
            <div className="board">
                <svg width={this.state.size} height={this.state.size} viewBox={`0 0 1 1`}>
                    <text x={0.04} y={0.04} style={{fill: "white", font: "normal 0.02px Optima"}}>Turn {this.props.turn} / 10</text>
                    <text x={0.04} y={0.06} style={{fill: "white", font: "normal 0.02px Optima"}}>{this.props.round}</text>
                    <image xlinkHref="/static/app/png/board.png" x="0" y="0" width="1" height="1"/>
                    <Storm sector={this.props.stormSector}/>
                    {this.getSpaceSectors()}
                    {this.getLogos()}
                    {this.getSpice()}
                    {this.getTokenPiles()}
                </svg>
            </div>
        );
    }
}


module.exports = Board;
