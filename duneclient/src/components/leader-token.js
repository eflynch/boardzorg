import React from 'react';

class LeaderToken extends React.Component {
    render () {
        return <img className={"leader-token" +
                               (this.props.traitor ? " traitor": "") +
                               (this.props.dead ?  " dead" : " alive") +
                               (this.props.onClick ? " active" : "") +
                               (this.props.selected ? " selected" : "")}
            src={"/static/app/png/Leader-" + this.props.name + ".png"}
            onClick={this.props.onClick}
            width={75} />;
    }
}


module.exports = LeaderToken;
