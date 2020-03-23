import React from 'react';

class Header extends React.Component {
    render () {
        return (
            <div className="main-header">
                <span className="site-title">SHAI-HULUD</span>
                <span className="session-title">{this.props.sessionTitle}</span>
                <span className="header-button" onClick={()=>{this.props.newSession()}}>New Session</span>
            </div>
        );
    }
}

module.exports = Header;
