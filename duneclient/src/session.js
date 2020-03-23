import React from 'react';
import ReactDOM from 'react-dom';

import Board from './board';
import Faction from './faction';
import History from './history';

import Bidding from './rounds/bidding';


class Session extends React.Component {
    getRoundState(round_state) {
        let state = null;
        if (round_state && round_state.round == "bidding"){
            state = <Bidding roundstate={round_state}/>;
        }
        if (state === null){
            return <div>{JSON.stringify(round_state)}</div>;
        }
        return <div className="roundstate">{state}</div>;
    }

    render () {
        let {state, actions, history} = this.props.data;
        console.log(state);
        let fs = Object.keys(state.faction_state);
        let factions = [];
        fs.forEach((faction) => {
            if (faction == this.props.me){
                return;
            }
            factions.push(<Faction key={faction} me={this.props.me} faction={faction} factionstate={state.faction_state[faction]}/>);
        });
        const logoPositions = fs.map((faction) => {
            let factionstate = state.faction_state[faction];
            return [factionstate.name, factionstate.token_position];
        });
        console.log(logoPositions);
        const stageTitle = `${state.round_state.round}${state.round_state.stage ? " : " + state.round_state.stage : ""}`;

        return (
            <div className="session">
                <Board turn={state.turn} boardstate={state.map_state} logoPositions={logoPositions}
                       stormSector={state.storm_position}/>
                <History stageTitle={stageTitle} error={this.props.error} actions={actions} sendCommand={this.props.sendCommand} commandLog={history}/>
                <Faction key={"me"} me={this.props.me} faction={this.props.me} factionstate={state.faction_state[this.props.me]}/>
                {this.getRoundState(state.round_state)}
                {factions}
            </div>
        );
    }
}


module.exports = Session;