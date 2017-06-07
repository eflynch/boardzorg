import React from 'react';
import $ from 'jquery';
import {render} from 'react-dom';

import App from './app'


document.addEventListener("DOMContentLoaded", function (){
  $.getJSON("/api/sessions/1", {faction: window.bootstrap.faction}, function(data){
    render(<App me={window.bootstrap.faction} data={data}/>, document.getElementById("content"))
  })
});
