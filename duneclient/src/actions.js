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
        const actionNames = Object.keys(this.props.actions);
        var actions = actionNames.map(function(actionName, i){
            return (
                <button key={i} onClick={
                        function(){
                            this.handle_click(actionName);
                        }.bind(this)} key={i}>
                    {actionName}
                </button>
            );
        }.bind(this));
        return (
            <div className="actions">
                {actions}
                <input type="text" ref="text"/>
                {error}
            </div>
        );
    }
}

module.exports = Actions;
