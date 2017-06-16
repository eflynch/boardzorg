import React from 'react';
import ReactDOM from 'react-dom';

import Board from './board';

class Faction extends React.Component {
    render () {
        return (
            <div>
                <h2>{this.props.faction}</h2>
                {JSON.stringify(this.props.factionstate)}
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
        return (
            <div>
                <h1>Dune</h1>
                <Board boardstate={this.props.gamestate.map_state}/>
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
            <div>
                <h1>Actions</h1>
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
