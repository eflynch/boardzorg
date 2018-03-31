import React from 'react';
import ReactDOM from 'react-dom';


class Actions extends React.Component {
    handle_click (action) {
        var args = ReactDOM.findDOMNode(this.refs.text);
        this.props.sendCommand(action + " " + args.value)
    }

    render () {
        let error = <span/>;
        if (this.props.error !== null && this.props.error !== undefined){
            if (this.props.error.BadCommand !== undefined){
                error = <span className="error">{this.props.error.BadCommand}</span>;
            }
            if (this.props.error.InvalidCommand !== undefined){
                error = <span className="error">{this.props.error.InvalidCommand}</span>;
            }
            if (this.props.error.UnhandledError !== undefined){
                error = <span className="error">{this.props.error.UnhandledError}</span>;
            }
        }
        var actions = this.props.actions.map(function(action, i){
            return (
                <li key={i}>
                    <span onClick={
                        function(){
                            this.handle_click(action);
                        }.bind(this)} key={i}>
                        {action}
                    </span>
                </li>
            );
        }.bind(this));
        return (
            <div className="actions">
                <ul>
                    {actions}
                    {error}
                    <input type="text" ref="text"/>
                </ul>
            </div>
        );
    }
}

module.exports = Actions;
