import React from 'react';
import ReactDOM from 'react-dom';

import {spice_location, token_location} from './board-data';

class Spice extends React.Component {
    render () {
        return (
            <div>
                <img src="static/app/png/melange.png"
                    style={{
                        position: "absolute",
                        top: this.props.scale * spice_location[this.props.space].top,
                        left: this.props.scale *spice_location[this.props.space].left,
                    }}
                    width={this.props.scale * 0.08}
                />
                <span style={{
                    position: "absolute",
                    top: this.props.scale * (spice_location[this.props.space].top + 0.01),
                    left: this.props.scale * (spice_location[this.props.space].left + 0.03),
                    color: "yellow",
                    fontWeight: 900,
                    fontFamily: "sans-serif"
                }}>{this.props.amount}</span>
            </div>
        )
    }
}

class TokenPile extends React.Component {
    getTokenPile (number, faction, space, sector) {
        let tokens = [];
        for (let i=0; i < number; i++){
            tokens.push(
                <img src={"static/app/png/" + this.props.faction + "_token.png"}
                 style={{
                    position: "absolute",
                    top: this.props.scale * (token_location[this.props.space][this.props.sector].top - 0.005*i),
                    left: this.props.scale * token_location[this.props.space][this.props.sector].left,
                 }}
                 width={this.props.scale * 0.05}
                 key={i}
                 />
            );
        }
        return tokens;
    }
    render () {
        return (
            <div>
                {this.getTokenPile(this.props.number, this.props.faction, this.props.space, this.props.sector)}
                <span style={{
                    position: "absolute",
                    top: this.props.scale * (token_location[this.props.space][this.props.sector].top - 0.005*this.props.number - 0.02),
                    left: this.props.scale * (token_location[this.props.space][this.props.sector].left - 0.030),
                    color: "black",
                    width: this.props.scale * 0.2,
                    fontWeight: 900,
                    textShadow: "0px 0px 2px white, 0 0 25px yellow, 0 0 5px orange",
                    fontFamily: "sans-serif",
                    textAlign: "right",
                    fontSize: 6
                }}>{this.props.number}</span>
            </div>
        );
    }
}

class Board extends React.Component {
    constructor(props) {
      super(props);
      this.state = { width: '0', height: '0' };
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
      this.setState({ width: window.innerWidth, height: window.innerHeight });
    }

    render () {
        let spice = [];
        let tokens = [];
        for (let i=0; i < this.props.boardstate.length; i++){
            let space = this.props.boardstate[i];
            if (space.spice){
                spice.push(<Spice key={space.name} scale={this.state.width} space={space.name} amount={space.spice}/>);
            }
            if (space.forces !== null){
                for (var faction in space.forces){
                    if (space.forces.hasOwnProperty(faction)){
                        for (var sector in space.forces[faction]){
                            if (space.forces[faction].hasOwnProperty(sector)){
                                tokens.push(
                                    <TokenPile key={space.name}
                                               number={space.forces[faction][sector].length}
                                               scale={this.state.width}
                                               space={space.name}
                                               sector={sector}
                                               faction={faction}/>);
                            }
                        }
                    }
                }
            }
        }
        return (
            <div>
                <div style={{
                    backgroundImage: "url(static/app/png/board.png)",
                    backgroundPosition: 'center center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: 'contain',
                    height: this.state.width,
                    width: this.state.width,
                    position: "relative"
                }}>
                {tokens}
                {spice}
                </div>
                {JSON.stringify(this.props.boardstate)}
            </div>
        );
    }
}


module.exports = Board
