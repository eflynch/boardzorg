import React from 'react';
import ReactDOM from 'react-dom';

class Board extends React.Component {
    constructor(props) {
      super(props);
      this.state = { width: '0', height: '0' };
      this.updateWindowDimensions = this.updateWindowDimensions.bind(this);
    }

    componentDidMount() {
      this.updateWindowDimensions();
      window.addEventListener('resize', this.updateWindowDimensions);
    }

    componentWillUnmount() {
      window.removeEventListener('resize', this.updateWindowDimensions);
    }

    updateWindowDimensions() {
      this.setState({ width: window.innerWidth, height: window.innerHeight });
    }

    render () {
        return (
            <div>
                <div style={{
                    backgroundImage: "url(static/app/png/board.png)",
                    backgroundPosition: 'center center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: 'contain',
                    height: this.state.width,
                    width: this.state.width,
                    position: "relative"
                }}>
                    <span style={{
                        position: "absolute",
                        top: this.state.width * 0.5,
                        left: this.state.width * 0.5
                    }}>test</span>
                </div>
                {JSON.stringify(this.props.boardstate)}
            </div>
        );
    }
}


module.exports = Board
