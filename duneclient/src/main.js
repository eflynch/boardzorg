import React from 'react';
import $ from 'jquery';
import {render} from 'react-dom';

import App from './app'
import Session from './session'


function sendCommand(session_id, faction, cmd){
    $.ajax({
        type: "POST",
        url: "/api/sessions/" + session_id,
        data: JSON.stringify({faction: faction, cmd: cmd}),
        success: function(data){
            console.log(data)
            render(<Session me={faction} data={data} sendCommand={function(cmd){
                sendCommand(session_id, faction, cmd);
            }}/>, document.getElementById("content"));
        },
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
}

function renderSession(session_id, faction){
    $.getJSON("/api/sessions/" + session_id, {faction: faction}, function(data){
        render(<Session me={faction} data={data} sendCommand={function(cmd){
            sendCommand(session_id, faction, cmd);
        }}/>, document.getElementById("content"));
    });
}

document.addEventListener("DOMContentLoaded", function (){
    // render(<App/>, document.getElementById("content"));
    renderSession(1, "bene-gesserit");
});
