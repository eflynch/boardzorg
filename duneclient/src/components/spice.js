import React from 'react';

class Spice extends React.Component {
    render () {
        return (
            <div style={{position:"relative"}}>
                <img src={"/static/app/png/melange_" + Math.ceil(this.props.amount/3) + ".png"}
                    width={this.props.width}
                    style={{"position": "absolute", top:0, left:0}}
                />
                <span style={{
                    position: "absolute",
                    top: this.props.width*0.50,
                    left: this.props.width*0.50,
                    color: "yellow",
                    fontWeight: 900,
                    fontFamily: "sans-serif"
                }}>{this.props.amount}</span>
            </div>
        )
    }
}

module.exports = Spice;