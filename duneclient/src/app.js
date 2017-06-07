import React from 'react';

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
                <h1>Game State</h1>
                {factions}
            </div>
        );
    }
}

class Actions extends React.Component {
    render () {
        var actions = this.props.actions.map(function(action, i){
            return <li key={i}>{action}</li>;
        });
        return (
            <div>
                <h1>Actions</h1>
                <ul>
                    {actions}
                </ul>
            </div>
        );
    }
}

class App extends React.Component {
    render () {
        return (
            <div>
                <Game me={this.props.me} gamestate={this.props.data.gamestate}/>
                <Actions actions={this.props.data.actions}/>
            </div>
        );
    }
}

module.exports = App;
