import React from 'react';

class Header extends React.Component {
    render () {
        const roleText = this.props.role ? <span className="session-role">{`(${this.props.role[0].toUpperCase() + this.props.role.slice(1)})`}</span> : "";
        return (
            <div className={"main-header"}>
                <a className="site-title" href="/">boardzorg.org</a>
                <span className="session-title">{this.props.sessionTitle}{roleText}</span>
            </div>
        );
    }
}

module.exports = Header;
