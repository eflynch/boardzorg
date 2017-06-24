import React from 'react';
import ReactDOM from 'react-dom';

import {spice_location, token_location, logo_position} from './board-data';

class Positioner extends React.Component {
    render () {
        return <div style={{
            position: "absolute",
            top: this.props.scale * this.props.location.top,
            left: this.props.scale * this.props.location.left
        }}>
            {this.props.children}
        </div>;
    }
}

class Spice extends React.Component {
    render () {
        return (
            <div style={{position:"relative"}}>
                <img src={"static/app/png/melange_" + Math.ceil(this.props.amount/3) + ".png"}
                    width={this.props.width}
                    style={{"position": "absolute", top:0, left:0}}
                />
                <span style={{
                    position: "absolute",
                    top: this.props.width*0.50,
                    left: this.props.width*0.50,
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
                width={this.props.width}
            />
        )
    }
}

class TokenPile extends React.Component {
    getTokenPile (number, faction) {
        let verticalOffset = this.props.height ? this.props.height - (76/142*this.props.width) : 0;
        let tokens = [];
        for (let i=0; i < number; i++){
            let path = "static/app/png/" + this.props.faction;
            path += (this.props.faction === "bene-gesserit" && this.props.coexist) ? "_coexist_token.png" : "_token.png";
            tokens.push(
                <img src={path} width={this.props.width} key={i}
                     style={{
                        position: "absolute",
                        top: -0.12 * this.props.width * i + verticalOffset,
                        left: 0
                     }}/>
            );
        }
        return tokens;
    }
    render () {
        let bonus = this.props.bonus ? " (+" + this.props.bonus + ")" : "";
        let verticalOffset = this.props.height ? this.props.height - (76/142*this.props.width) : 0;
        return (
            <div style={{position:"relative"}}>
                {this.getTokenPile(this.props.number, this.props.faction)}
                <span style={{
                    position: "absolute",
                    top: this.props.width * (-0.12 * this.props.number - 0.4) + verticalOffset,
                    left: -this.props.width / 2,
                    color: "black",
                    width: this.props.width * 2,
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
                    let location = token_location[space.name][sector][orders[space.name]];
                    tokens.push(
                        <Positioner key={space.name + sector + faction}scale={this.state.width} location={location}>
                            <TokenPile number={number}
                                       bonus={number !== power ? power - number : null}
                                       width={this.state.width * 0.05}
                                       coexist={space.coexist}
                                       faction={faction}/>
                        </Positioner>);
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
            spice.push(
                <Positioner key={space.name+"spice"} scale={this.state.width} location={spice_location[space.name]}>
                    <Spice amount={space.spice} width={this.state.width * 0.08} space={space.name}/>
                </Positioner>
            );
        }
        return spice;
    }

    getLogos () {
        let logos = [];
        for (let i=0; i < this.props.logoPositions.length; i++){
            let faction = this.props.logoPositions[i][0];
            let position = this.props.logoPositions[i][1];
            if (position === null){
                continue;
            }
            logos.push(<Positioner key={faction+"logo"} scale={this.state.width} location={logo_position[position]}>
                <Logo width={this.state.width * 0.05} faction={faction}/>
            </Positioner>);
        }
        return logos;
    }

    render () {
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
                {this.getLogos()}
                {this.getSpice()}
                {this.getTokenPiles()}
                </div>
            </div>
        );
    }
}


module.exports = {
    Board: Board,
    TokenPile: TokenPile,
    Spice: Spice
}
