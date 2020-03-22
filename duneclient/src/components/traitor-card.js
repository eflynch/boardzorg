import React from 'react';

class TraitorCard extends React.Component {
    render () {
        return <img style={{float: "left"}}
            src={"/static/app/png/Traitor-" + this.props.name + ".png"}
            width={150} />;
    }
}

module.exports = TraitorCard;
