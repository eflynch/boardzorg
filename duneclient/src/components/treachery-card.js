import React from 'react';

import {randInt} from '../utils';

class TreacheryCard extends React.Component {
    render () {
        let name = this.props.name;
        if (this.props.name === "Cheap-Hero/Heroine"){
            name = ["Cheap-Hero", "Cheap-Heroine"][randInt(0,1)];
        }
        return <img
            src={"/static/app/png/Treachery-" + name.replace(" ", "-") + ".png"}
            width={150} />;
    }
}

module.exports = TreacheryCard;
