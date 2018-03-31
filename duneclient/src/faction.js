import React from 'react';

import TokenPile from './components/token-pile';
import Spice from './components/spice';
import TraitorCard from './components/traitor-card';
import TreacheryCard from './components/treachery-card';
import LeaderToken from './components/leader-token';


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
    getBribeSpice () {
        if (this.props.factionstate.bribe_spice !== undefined){
            return <div style={{float:"left", width: 75, height: 75}}>
                <Spice width={75} amount={this.props.factionstate.bribe_spice}/>
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
                {this.getBribeSpice()}
            </div>
        );
    }
}

module.exports = Faction;
