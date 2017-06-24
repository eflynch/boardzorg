import React from 'react';
import $ from 'jquery';
import {render} from 'react-dom';

import Header from './header'
import Session from './session'

var last_faction;
var last_data;
var last_session_id;

function renderSession(session_id, faction, data){
    last_faction = faction;
    last_data = data;
    last_session_id = session_id;
    render(<Session me={faction} data={data} error={null} sendCommand={function(cmd){
        sendCommand(session_id, faction, cmd);
    }}/>, document.getElementById("content"));
}

function renderError(error){
    render(<Session me={last_faction} data={last_data} error={error} sendCommand={function(cmd){
        sendCommand(last_session_id, last_faction, cmd);
    }}/>, document.getElementById("content"));
}

function sendCommand(session_id, faction, cmd){
    $.ajax({
        type: "POST",
        url: "/api/sessions/" + session_id,
        data: JSON.stringify({faction: faction, cmd: cmd}),
        success: function(data){
            renderSession(session_id, faction, data);
        },
        error: function(data){
            renderError(data.responseJSON);
        },
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
}

function getSession(session_id, faction){
    $.getJSON("/api/sessions/" + session_id, {faction: faction}, function(data){
        renderSession(session_id, faction, data);
    });
}

document.addEventListener("DOMContentLoaded", function (){
    render(<Header getSession={getSession}/>, document.getElementById("header"));
    getSession(1, "guild");
});
