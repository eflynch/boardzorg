import React from 'react';

class LeaderToken extends React.Component {
    render () {
        return <img className={this.props.dead ?  "dead" : "alive"}
            src={"static/app/png/Leader-" + this.props.name + ".png"}
            width={75} />;
    }
}


module.exports = LeaderToken;
