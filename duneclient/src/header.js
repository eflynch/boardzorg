import React from 'react';

const SESSION_ID = 1;

var FactionButton = function(props){
    return <li onClick={()=>{
        props.getSession(SESSION_ID, props.faction);
    }}>{props.faction}</li>;
}

class Header extends React.Component {
    render () {
        return (
            <ul>
                <FactionButton faction="guild" getSession={this.props.getSession}/>
                <FactionButton faction="emperor" getSession={this.props.getSession}/>
                <FactionButton faction="atreides" getSession={this.props.getSession}/>
                <FactionButton faction="harkonnen" getSession={this.props.getSession}/>
                <FactionButton faction="bene-gesserit" getSession={this.props.getSession}/>
                <FactionButton faction="fremen" getSession={this.props.getSession}/>
            </ul>
        );
    }
}

module.exports = Header;
