import React from 'react';
import ReactDOM from 'react-dom';

import {spice_location, token_location, logo_position} from './board-data';

class Spice extends React.Component {
    render () {
        return (
            <div>
                <img src={"static/app/png/melange_" + Math.ceil(this.props.amount/3) + ".png"}
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

class Storm extends React.Component {
    render () {
        return <img
            src={"static/app/png/storm_" + this.props.sector + ".png"}
            style={{
                position: "absolute",
                top: 0,
                left: 0,
                opacity: 0.9
            }}
            width={this.props.scale}
        />;
    }
}

class Logo extends React.Component {
    render () {
        return (
            <img src={"static/app/png/" + this.props.faction + "_logo.png"}
                style={{
                    position: "absolute",
                    top: this.props.scale * (logo_position[this.props.position].top),
                    left: this.props.scale * (logo_position[this.props.position].left)
                }}
                width={this.props.scale * 0.05}
            />
        )
    }
}

class TokenPile extends React.Component {
    getLocation () {
        if (this.props.location) return this.props.location;
        return token_location[this.props.space][this.props.sector][this.props.order];
    }
    getTokenPile (number, faction) {
        let tokens = [];
        for (let i=0; i < number; i++){
            let path = "static/app/png/" + this.props.faction;
            path += (this.props.faction === "bene-gesserit" && this.props.coexist) ? "_coexist_token.png" : "_token.png";
            tokens.push(
                <img src={path}
                 style={{
                    position: "absolute",
                    top: this.props.scale * (this.getLocation().top - 0.005*i),
                    left: this.props.scale * this.getLocation().left,
                 }}
                 width={this.props.scale * 0.05}
                 key={i}
                 />
            );
        }
        return tokens;
    }
    render () {
        let bonus = this.props.bonus ? " (+" + this.props.bonus + ")" : "";
        return (
            <div>
                {this.getTokenPile(this.props.number, this.props.faction)}
                <span style={{
                    position: "absolute",
                    top: this.props.scale * (this.getLocation().top - 0.005*this.props.number - 0.02),
                    left: this.props.scale * (this.getLocation().left),
                    color: "black",
                    width: this.props.scale * 0.05,
                    fontWeight: 900,
                    textShadow: "0 0 3px white, 0 0 15px yellow, 0 0 5px red",
                    fontFamily: "sans-serif",
                    textAlign: "center",
                    fontSize: 16
                }}>{this.props.number + bonus}</span>
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
      this.setState({ width: Math.min(window.innerWidth, 800), height: window.innerHeight });
    }

    render () {
        let spice = [];
        let tokens = [];
        let orders = {};
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
                                if (orders.hasOwnProperty(space.name)){
                                    orders[space.name] += 1;
                                } else {
                                    orders[space.name] = 1;
                                }
                                let number = space.forces[faction][sector].length;
                                let power = space.forces[faction][sector].reduce((a, b) => a + b, 0);
                                tokens.push(
                                    <TokenPile key={space.name + sector + faction}
                                               number={number}
                                               bonus={number !== power ? power - number : null}
                                               scale={this.state.width}
                                               space={space.name}
                                               sector={sector}
                                               coexist={space.coexist}
                                               order={orders[space.name]}
                                               faction={faction}/>);
                            }
                        }
                    }
                }
            }
        }
        let logos = [];
        for (let i=0; i < this.props.logoPositions.length; i++){
            let faction = this.props.logoPositions[i][0];
            let position = this.props.logoPositions[i][1];
            if (position !== null){
                logos.push(<Logo key={faction} scale={this.state.width} faction={faction} position={position}/>);
            }
        }
        return (
            <div className="board">
                <div style={{
                    backgroundImage: "url(static/app/png/board.png)",
                    backgroundPosition: 'center center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: 'contain',
                    height: this.state.width,
                    width: this.state.width,
                    position: "relative",
                    margin: 0
                }}>
                <Storm scale={this.state.width} sector={this.props.stormSector}/>
                {tokens}
                {spice}
                {logos}
                </div>
            </div>
        );
    }
}


module.exports = {
    Board: Board,
    TokenPile: TokenPile
}
