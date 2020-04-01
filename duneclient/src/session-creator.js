import React from 'react';

class SessionCreator extends React.Component {
    constructor(props){
        super(props);
        this.state = {"input": ""}
    }
    render () {
        return (
            <div className="sessioncreator">
                <input value={this.state.input} onChange={(e)=>{
                    this.setState({input: e.target.value});
                }}/>
                <button onClick={()=>{this.props.newSession(this.state.input)}}>New Session</button>
            </div>
        );
    }
}

module.exports = SessionCreator;
