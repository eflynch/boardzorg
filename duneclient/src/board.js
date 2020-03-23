import React from 'react';
import ReactDOM from 'react-dom';

import {spice_location, token_location, logo_position} from './board-data';

import Spice from './components/spice';
import TokenPile from './components/token-pile';


const Storm = ({sector}) => {
    return <image xlinkHref={`/static/app/png/storm_${sector}.png`} x="0" y="0" width="1" height="1" opacity={0.8}/>;
};

const Logo = ({faction, diameter, x, y}) => {
    return <image xlinkHref={`/static/app/png/${faction}_logo.png`} x={x} y={y} width={diameter} height={diameter}/>;
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
                    let {left, top} = token_location[space.name][sector][orders[space.name]];
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
            const {left, top} = spice_location[space.name];
            spice.push(
                <Spice key={space.name+"spice"} x={left} y={top} amount={space.spice} width={0.08} height={0.08}/>
            );
        }
        return spice;
    }

    getLogos () {
        let logos = [];
        return this.props.logoPositions.map((pos) => {
            const [faction, position] = pos;
            const {top, left} = logo_position[position];
            return <Logo key={faction} diameter={0.05} faction={faction} x={left} y={top}/>;
        });
    }

    render () {
        return (
            <div className="board">
                <svg width={this.state.size} height={this.state.size} viewBox={`0 0 1 1`}>
                    <text x={0.04} y={0.04} style={{fill: "white", font: "normal 0.02px Optima"}}>Turn: {this.props.turn} / 10 ({this.props.stageTitle})</text>
                    <image xlinkHref="/static/app/png/board.png" x="0" y="0" width="1" height="1"/>
                    <Storm sector={this.props.stormSector}/>
                    {this.getLogos()}
                    {this.getSpice()}
                    {this.getTokenPiles()}
                </svg>
            </div>
        );
    }
}


module.exports = Board;
