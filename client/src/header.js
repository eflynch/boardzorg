import React from 'react';

class Header extends React.Component {
    render () {
        const roleText = this.props.role ? ` : ${this.props.role}` : "";
        return (
            <div className={"main-header" + (this.props.blocking ? " blocking" : "")}>
                <a className="site-title" href="/">SHAI-HULUD</a>
                <span className="session-title">{this.props.sessionTitle}{roleText}</span>
            </div>
        );
    }
}

module.exports = Header;
