import React from 'react';

class Header extends React.Component {
    render () {
        return (
            <div className="main-header">
                <a className="site-title" href="/">SHAI-HULUD</a>
                <span className="session-title">{this.props.sessionTitle} : {this.props.role}</span>
            </div>
        );
    }
}

module.exports = Header;
