import React from 'react';


class SpiceCard extends React.Component {
    render () {
        return <img
            src={"static/app/png/Spice-" + this.props.name + ".png"}
            width={150} />;
    }
}

module.exports = SpiceCard;
