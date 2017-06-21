import React from 'react';
import ReactDOM from 'react-dom';

import {Board, TokenPile} from './board';


class SpiceCard extends React.Component {
    render () {
        return <img
            src={"static/app/png/Spice-" + this.props.name + ".png"}
            width={150} />;
    }
}


class TreacheryCard extends React.Component {
    render () {
        return <img
            src={"static/app/png/Treachery-" + this.props.name + ".png"}
            width={150} />;
    }
}

class TraitorCard extends React.Component {
    render () {
        return <img
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
            return this.props.factionstate.treachery.map((name) => {
                return <TreacheryCard key={name} name={name} />;
            });
        } else {
            let treachery = [];
            for (let i=0; i < this.props.factionstate.treachery.length; i++){
                treachery.push(<TreacheryCard key="Reverse" name="Reverse" />);
            }
            return treachery;
        }
    }
    getTraitors () {
        if (this.props.me !== this.props.faction){
            return [];
        }
        return this.props.factionstate.traitors.map((traitor) => {
            return <TraitorCard key={traitor[0]} name={traitor[0]} />;
        });
    }
    getLeaders () {
        return <div style={{width:150, float:"left"}}>
            {this.props.factionstate.leaders.map((leader) => {
                let dead = false;
                if (this.props.factionstate.tank_leaders.indexOf(leader) !== -1){
                    dead = true;
                }
            return <LeaderToken key={leader[0]} name={leader[0]} dead={dead}/>;
            })}
        </div>;
    }
    getTokens () {
        let number = this.props.factionstate.reserve_units.length;
        let power = this.props.factionstate.reserve_units.reduce((a, b) => a + b, 0);
        return <div style={{float:"left", position:"relative", width: 45, height: 225}}>
            <TokenPile scale={800} location={{top:0.25, left:0.002}} faction={this.props.faction} number={number} bonus={power-number}/>
        </div>;
    }
    render () {


        return (
            <div style={{float: "left", border: "1px solid red"}}>
                <h2>{this.props.faction}</h2>
                {this.getTreachery()}
                {this.getTraitors()}
                {this.getLeaders()}
                {this.getTokens()}
            </div>
        );
    }
}

class Game extends React.Component {
    render () {
        var fs = Object.keys(this.props.gamestate.faction_state);
        var factions = fs.map((faction) => {
            return <Faction key={faction} me={this.props.me} faction={faction} factionstate={this.props.gamestate.faction_state[faction]}/>;
        });
        var logoPositions = fs.map((faction) => {
            let factionstate = this.props.gamestate.faction_state[faction];
            return [factionstate.name, factionstate.token_position];
        });
        return (
            <div>
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
            <div style={{float:"left"}}>
                <input type="text" ref="text"/>
                <ul>
                    {actions}
                </ul>
            </div>
        );
    }
}

class Session extends React.Component {
    render () {
        return (
            <div>
                <Game me={this.props.me} gamestate={this.props.data.state}/>
                <Actions actions={this.props.data.actions} sendCommand={this.props.sendCommand}/>
            </div>
        );
    }
}

module.exports = Session;
