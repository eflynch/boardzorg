import React, {useState} from 'react';
import update from 'immutability-helper';

const Choice = ({args, setArgs}) => {
    return (
        <div>
            {args.map((arg, i) => {
                return (
                    <div>
                        <Widget key={i} type={arg.widget} args={arg.args} setArgs={setArgs}/>
                    </div>
                );
            })}
        </div>
    );
};

const Struct = ({args, setArgs}) => {
    const initialState = Array(args.length).fill("");
    args.forEach((arg, i) => {
        if (arg.widget === "constant") {
            initialState[i] = arg.args;
        }
    });
    const [subArgs, setSubArgs] = useState(initialState);
    return (
        <div>
            {args.map((arg, i) => {
                return <Widget key={i} type={arg.widget} args={arg.args} setArgs={(args)=> {
                    const newSubArgs = update(subArgs, {[i]: {$set: args}});
                    setSubArgs(newSubArgs);
                    setArgs(newSubArgs.join(" "));
                }}/>
            })}
        </div>
    );
};

const Input = ({args, setArgs}) => {
    const [inputValue, setInputValue] = useState("");
    return <input value={inputValue} onChange={((e)=>{
        const value = e.target.value;
        setInputValue(value);
        setArgs(value);
    })}/>;
};

const Widget = ({type, args, setArgs}) => {
    if (type === "choice") {
        return <Choice args={args} setArgs={setArgs} />; 
    }

    if (type === "struct") {
        return <Struct args={args} setArgs={setArgs} />; 
    }

    if (type === "input") {
        return <Input args={args} setArgs={setArgs} />; 
    }

    if (type === "faction-select") {
        return <Input setArgs={setArgs} />;
    }

    if (type === "integer") {
        return <Input setArgs={setArgs} />;
    }

    if (type === "constant") {
        return args;
    }

    if (type === "units") {
        return <Input setArgs={setArgs} />;
    }

    if (type === "space-sector-select") {
        return <Input setArgs={setArgs} />;
    }

    if (type === "token-select") {
        return <Input setArgs={setArgs} />;
    }

    console.log(type);
};

const ActionArgs = ({sendCommand, actionName, argSpec}) => {
    const [args, setArgs] = useState("");
    return (
        <div>
            <Widget setArgs={setArgs} type={argSpec.widget} args={argSpec.args} />
            <button onClick={()=>{
                console.log(args);
                sendCommand(`${actionName} ${args}`);
            }}>Submit Command</button>
        </div>
    );
} 

class Actions extends React.Component {
    constructor(props) {
        super(props);
        this.state = {selectedAction: null};
    }

    render () {
        let {selectedAction} = this.state;
        let {error, actions, sendCommand} = this.props;
        let errordiv = <div/>;
        if (error !== null && error !== undefined){
            if (error.BadCommand !== undefined){
                errordiv = <div className="error">{error.BadCommand}</div>;
            }
            if (error.IllegalAction !== undefined){
                errordiv = <div className="error">{error.IllegalAction}</div>;
            }
            if (error.UnhandledError !== undefined){
                errordiv = <div className="error">{error.UnhandledError}</div>;
            }
        }
        const actionNames = Object.keys(actions);
        const actionButtons = actionNames.map((actionName, i) => {
            return (
                <li className={selectedAction === actionName ? "selected" : ""} key={i} onClick={()=>{this.setState({selectedAction: actionName});}} key={i}>
                    {actionName}
                </li>
            );
        });
        let actionArgs = <span/>;
        if (actionNames.indexOf(selectedAction) != -1) {
            actionArgs = <ActionArgs sendCommand={sendCommand} actionName={selectedAction} argSpec={actions[selectedAction]}/>
        }
        return (
            <div className="actions-wrapper">
                <div className="actions">
                    {actionButtons}
                </div>
                {actionArgs}
                {errordiv}
            </div>
        );
    }
}

module.exports = Actions;
