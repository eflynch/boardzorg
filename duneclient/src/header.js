import React from 'react';

var FactionButton = function(props){
    return <li onClick={()=>{
        props.getSession(props.faction);
    }}>{props.faction}</li>;
}

class Header extends React.Component {
    render () {
        return (
            <ul>
                <li onClick={()=>{this.props.newSession()}}>New Session</li>
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
