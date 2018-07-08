/* global document, fetch, window */
import React, {Component} from 'react';
import {render} from 'react-dom';
import MapGL from 'react-map-gl';
import DeckGLOverlay from './deckgl-overlay.js';

// Set your mapbox token here
const MAPBOX_TOKEN = "pk.eyJ1IjoibGl6aWhhbiIsImEiOiJjamkwYTUxOHUxNXRoM3BtcWo1Y3Y3NmJpIn0.tWeqa7wMJy35WHPVGF6TgA"; // eslint-disable-line

// Source data CSV
const DATA_URL = {
  BUILDINGS:
    'https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/trips/buildings.json', // eslint-disable-line
  TRIPS:
  'http://localhost:8080/fake_data/path.json' // eslint-disable-line
  //  'http://localhost:8080/311d1ab2eb8d49088849230c9f76a1b2/path.json' // eslint-disable-line
  //   'https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/trips/trips.json' // eslint-disable-line
};

class Root extends Component {
  constructor(props) {
    super(props);
    this.state = {
      viewport: {
        ...DeckGLOverlay.defaultViewport,
        width: 500,
        height: 500
      },
      buildings: null,
      trips: null,
      time: 0
    };

    fetch(DATA_URL.BUILDINGS)
      .then(resp => resp.json())
      .then(data => this.setState({buildings: data}));

    fetch(DATA_URL.TRIPS)
      .then(resp => resp.json())
      .then(data => this.setState({trips: data}));

    

  }

  componentDidMount() {
    window.addEventListener('resize', this._resize.bind(this));
    this._resize();
    this._animate();
  }

  componentWillUnmount() {
    if (this._animationFrame) {
      window.cancelAnimationFrame(this._animationFrame);
    }
  }

  _animate() {
    const timestamp = Date.now();
    const loopLength = 1800;
    const loopTime = 60000;

    this.setState({
      time: (timestamp % loopTime) / loopTime * loopLength
    });
    this._animationFrame = window.requestAnimationFrame(this._animate.bind(this));
  }

  _resize() {
    this._onViewportChange({
      width: window.innerWidth,
      height: window.innerHeight
    });
  }

  _onViewportChange(viewport) {
    this.setState({
      viewport: {...this.state.viewport, ...viewport}
    });
  }

  render() {
    const {viewport, buildings, trips, time} = this.state;
    //console.log(trips)
    return (
      <MapGL
        {...viewport}
        mapStyle="mapbox://styles/mapbox/dark-v9"
        onViewportChange={this._onViewportChange.bind(this)}
        mapboxApiAccessToken={MAPBOX_TOKEN}
      >
        <DeckGLOverlay
          viewport={viewport}
          buildings={buildings}
          trips={trips} // changed
          trailLength={180}
          time={time}
        />
      </MapGL>
    );
  }
}

render(<Root />, document.body.appendChild(document.createElement('div')));
