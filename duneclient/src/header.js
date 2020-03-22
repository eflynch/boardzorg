import React from 'react';

class Header extends React.Component {
    render () {
        return (
            <div className="main-header">
                <span className="site-title">Shai-Hulud</span>
                <span className="session-title">{this.props.sessionTitle}</span>
                <li onClick={()=>{this.props.newSession()}}>New Session</li>
            </div>
        );
    }
}

module.exports = Header;
