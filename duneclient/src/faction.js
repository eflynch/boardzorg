import React from 'react';

import TokenPile from './components/token-pile';
import Spice from './components/spice';
import Card from './components/card';
import LeaderToken from './components/leader-token';
import update from 'immutability-helper';


class Faction extends React.Component {
    getTreachery () {
        if (!this.props.factionstate.hasOwnProperty("treachery")){
            return [];
        }

        if (Array.isArray(this.props.factionstate.treachery)){
            return this.props.factionstate.treachery.map((name, i) => {
                return <Card type="Treachery" key={i} name={name} />;
            });
        } else {
            let treachery = [];
            for (let i=0; i < this.props.factionstate.treachery.length; i++){
                treachery.push(<Card type="Treachery" key={"reverse-"+i} name="Reverse" />);
            }
            return treachery;
        }
    }
    getLeaders () {
        return (
            <div style={{display:"flex", flexWrap:"wrap"}}>
                {this.props.factionstate.leaders.map((leader) => {
                    let dead = false;
                    if (this.props.factionstate.tank_leaders.indexOf(leader) !== -1){
                        dead = true;
                    }
                    return <LeaderToken key={"leader-"+leader[0]} name={leader[0]} dead={dead}/>;
                })}
            </div>
        );
    }
    getTraitors () {
        if (this.props.me !== this.props.faction){
            return [];
        }
        const interaction = this.props.interaction;
        const mode = interaction.mode;
        return this.props.factionstate.traitors.map((traitor) => {
            const traitorName = traitor[0];
            const selected = interaction["traitor-select"] == traitorName;
            const onClick = mode === "traitor-select" ? () => {
                this.props.setInteraction(update(
                    interaction,
                    {
                        [mode]: {$set: traitorName},
                        mode: {$set: null},
                    }
                ));
            } : null;
            return <Card type="Traitor"
                    key={"traitor-"+traitorName}
                    name={traitor[0]}
                    selected={selected}
                    onClick={onClick}/>;
        });
    }
    getTokens () {
        let number = this.props.factionstate.reserve_units.length;
        let power = this.props.factionstate.reserve_units.reduce((a, b) => a + b, 0);
        return <TokenPile width={50} faction={this.props.faction} number={number} bonus={power-number}/>
    }
    getSpice () {
        if (this.props.factionstate.spice !== undefined){
            return (
                <div style={{display: "flex", flexDirection: "column", alignItems:"center"}}>
                    Spice<Spice width={75} amount={this.props.factionstate.spice}/>
                </div>
            );
        }
        return <div/>;
    }
    getBribeSpice () {
        if (this.props.factionstate.bribe_spice !== undefined){
            return (
                <div style={{display: "flex", flexDirection: "column", alignItems:"center"}}>
                    Bribe<Spice width={75} amount={this.props.factionstate.bribe_spice}/>
                </div>
            );
        }
        return <div/>;
    }
    render () {
        return (
            <div className={"faction" + (this.props.me === this.props.faction ? " me" : "")}>
                <h2>{this.props.faction}</h2>
                {this.getLeaders()}
                {this.getTokens()}
                {this.getSpice()}
                <div style={{display:"flex", flexWrap: "wrap"}}>
                    {this.getTreachery()}
                    {this.getTraitors()}
                </div>
                {this.getBribeSpice()}
            </div>
        );
    }
}

module.exports = Faction;
