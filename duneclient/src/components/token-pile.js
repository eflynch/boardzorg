import React from 'react';


class TokenPile extends React.Component {
    getTokenPile (number, faction) {
        let verticalOffset = this.props.height ? this.props.height - (76/142*this.props.width) : 0;
        let tokens = [];
        for (let i=0; i < number; i++){
            let path = "/static/app/png/" + this.props.faction;
            path += (this.props.faction === "bene-gesserit" && this.props.coexist) ? "_coexist_token.png" : "_token.png";
            tokens.push(
                <img src={path} width={this.props.width} key={i}
                     style={{
                        position: "absolute",
                        top: -0.12 * this.props.width * i + verticalOffset,
                        left: 0
                     }}/>
            );
        }
        return tokens;
    }
    render () {
        let bonus = this.props.bonus ? " (+" + this.props.bonus + ")" : "";
        let verticalOffset = this.props.height ? this.props.height - (76/142*this.props.width) : 0;
        return (
            <div style={{position:"relative"}}>
                {this.getTokenPile(this.props.number, this.props.faction)}
                <span style={{
                    position: "absolute",
                    top: this.props.width * (-0.12 * this.props.number - 0.4) + verticalOffset,
                    left: -this.props.width / 2,
                    color: "black",
                    width: this.props.width * 2,
                    fontWeight: 900,
                    textShadow: "0 0 3px white, 0 0 15px yellow, 0 0 5px red",
                    fontFamily: "sans-serif",
                    textAlign: "center",
                    fontSize: 16
                }}>{this.props.number + bonus}</span>
            </div>
        );
    }
}

module.exports = TokenPile;
