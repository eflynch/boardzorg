import React from 'react';
import ReactDOM from 'react-dom';

import {Board, TokenPile, Spice} from './board';

function getRandomIntInclusive(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min; //The maximum is inclusive and the minimum is inclusive
}

class BiddingState extends React.Component {
    getCards () {
        let cards = [];
        let reverses = this.props.roundstate.up_for_auction.length;
        if (this.props.roundstate.up_for_auction.next !== undefined){
            cards.push(<TreacheryCard
                key="next" name={this.props.roundstate.up_for_auction.next}/>);
            reverses -=1;
        }
        for (let i=0; i<reverses;i++){
            cards.push(<TreacheryCard key={i} name="Reverse"/>);
        }
        return cards;
    }
    getBids () {
        return Object.keys(this.props.roundstate.stage_state.bids).map((faction) => {
            return (
                <li key={faction}>
                    {faction} : {this.props.roundstate.stage_state.bids[faction]}
                </li>
            );
        });
    }
    render () {
        if (this.props.roundstate.stage_state.stage === "auction"){
            return (
                <div>
                    <h4>Bidding Round</h4>
                    {this.getCards()}
                    {this.getBids()}
                </div>
            );
        }
        return <div/>;
    }
}

class RoundState extends React.Component {
    render () {
        let state = null;
        if (this.props.roundstate.round == "bidding"){
            state = <BiddingState roundstate={this.props.roundstate}/>;
        }
        if (state === null){
            return <div>{JSON.stringify(this.props.roundstate)}</div>;
        }
        return <div className="roundstate">{state}</div>;
    }
}


class SpiceCard extends React.Component {
    render () {
        return <img
            src={"static/app/png/Spice-" + this.props.name + ".png"}
            width={150} />;
    }
}


class TreacheryCard extends React.Component {
    render () {
        let name = this.props.name;
        if (this.props.name === "Cheap-Hero/Heroine"){
            name = ["Cheap-Hero", "Cheap-Heroine"][getRandomIntInclusive(0,1)];
        }
        return <img style={{float:"left"}}
            src={"static/app/png/Treachery-" + name + ".png"}
            width={150} />;
    }
}

class TraitorCard extends React.Component {
    render () {
        return <img style={{float: "left"}}
            src={"static/app/png/Traitor-" + this.props.name + ".png"}
            width={150} />;
    }
}

class LeaderToken extends React.Component {
    render () {
        return <img className={this.props.dead ?  "dead" : "alive"}
            src={"static/app/png/Leader-" + this.props.name + ".png"}
            width={75} />;
    }
}

class Faction extends React.Component {
    getTreachery () {
        if (!this.props.factionstate.hasOwnProperty("treachery")){
            return [];
        }

        if (Array.isArray(this.props.factionstate.treachery)){
            return this.props.factionstate.treachery.map((name, i) => {
                return <TreacheryCard key={i} name={name} />;
            });
        } else {
            let treachery = [];
            for (let i=0; i < this.props.factionstate.treachery.length; i++){
                treachery.push(<TreacheryCard key={"reverse-"+i} name="Reverse" />);
            }
            return treachery;
        }
    }
    getTraitors () {
        if (this.props.me !== this.props.faction){
            return [];
        }
        return this.props.factionstate.traitors.map((traitor) => {
            return <TraitorCard key={"traitor-"+traitor[0]} name={traitor[0]} />;
        });
    }
    getLeaders () {
        return <div style={{width:150, float:"left"}}>
            {this.props.factionstate.leaders.map((leader) => {
                let dead = false;
                if (this.props.factionstate.tank_leaders.indexOf(leader) !== -1){
                    dead = true;
                }
            return <LeaderToken key={"leader-"+leader[0]} name={leader[0]} dead={dead}/>;
            })}
            {this.getSpice()}
        </div>;
    }
    getTokens () {
        let number = this.props.factionstate.reserve_units.length;
        let power = this.props.factionstate.reserve_units.reduce((a, b) => a + b, 0);
        return <div style={{float:"left", width: 50, height: 210}}>
            <TokenPile width={50} height={210} faction={this.props.faction} number={number} bonus={power-number}/>
        </div>;
    }
    getSpice () {
        if (this.props.factionstate.spice !== undefined){
            return <div style={{float:"left", width: 75, height: 75}}>
                <Spice width={75} amount={this.props.factionstate.spice}/>
            </div>;
        }
        return <div/>;
    }
    render () {
        return (
            <div style={{float: "left", border: "1px solid red"}}>
                <h2>{this.props.faction}</h2>
                {this.getLeaders()}
                {this.getTokens()}
                {this.getTreachery()}
                {this.getTraitors()}
            </div>
        );
    }
}

class Game extends React.Component {
    render () {
        let fs = Object.keys(this.props.gamestate.faction_state);
        let factions = [];
        fs.forEach((faction) => {
            if (faction == this.props.me){
                return;
            }
            factions.push(<Faction key={faction} me={this.props.me} faction={faction} factionstate={this.props.gamestate.faction_state[faction]}/>);
        });
        var logoPositions = fs.map((faction) => {
            let factionstate = this.props.gamestate.faction_state[faction];
            return [factionstate.name, factionstate.token_position];
        });
        return (
            <div>
                <Faction key={"me"} me={this.props.me} faction={this.props.me} factionstate={this.props.gamestate.faction_state[this.props.me]}/>
                <RoundState roundstate={this.props.gamestate.round_state}/>
                <Board boardstate={this.props.gamestate.map_state} logoPositions={logoPositions}
                stormSector={this.props.gamestate.storm_position}/>
                {factions}
            </div>
        );
    }
}

class Actions extends React.Component {
    handle_click (action) {
        var args = ReactDOM.findDOMNode(this.refs.text);
        this.props.sendCommand(action + " " + args.value)
    }

    render () {
        let error = <span/>;
        if (this.props.error !== null){
            if (this.props.error.BadCommand !== undefined){
                error = <span className="error">{this.props.error.BadCommand}</span>;
            }
            if (this.props.error.InvalidCommand !== undefined){
                error = <span className="error">{this.props.error.InvalidCommand}</span>;
            }
            if (this.props.error.UnhandledError !== undefined){
                error = <span className="error">{this.props.error.UnhandledError}</span>;
            }
        }
        var actions = this.props.actions.map(function(action, i){
            return (
                <li key={i}>
                    <span onClick={
                        function(){
                            this.handle_click(action);
                        }.bind(this)} key={i}>
                        {action}
                    </span>
                </li>
            );
        }.bind(this));
        return (
            <div className="actions">
                <ul>
                    {actions}
                    {error}
                    <input type="text" ref="text"/>
                </ul>
            </div>
        );
    }
}

class Session extends React.Component {
    render () {
        return (
            <div>
                <Actions error={this.props.error} actions={this.props.data.actions} sendCommand={this.props.sendCommand}/>
                <Game me={this.props.me} gamestate={this.props.data.state}/>
            </div>
        );
    }
}

module.exports = Session;
