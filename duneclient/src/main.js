import React from 'react';
import $ from 'jquery';
import {render} from 'react-dom';

import Header from './header'
import Session from './session'

var last_data;
var last_session_id = sessionStorage.getItem('last_session_id');


function renderSession(session_id, faction, data, error){
    if (session_id === null || session_id === undefined){
        return;
    }
    last_data = data;
    sessionStorage.setItem('last_session_id', last_session_id);
    render(<Session me={faction} data={data} error={error} sendCommand={function(cmd){
        sendCommand(session_id, faction, cmd);
    }}/>, document.getElementById("content"));
}

function sendCommand(session_id, faction, cmd){
    $.ajax({
        type: "POST",
        url: "/api/sessions/" + session_id,
        data: JSON.stringify({faction: faction, cmd: cmd}),
        success: function(data){
            renderSession(session_id, faction, data, null);
        },
        error: function(data){
            renderSession(session_id, faction, last_data, data.responseJSON);
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

function newSession(){
    $.ajax({
        type: "POST",
        url: "/api/sessions",
        success: function(data){
            console.log(data);
            getSession(data.id, "guild");
        },
        error: function(data){
            console.log("shit!");
        },
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
}

document.addEventListener("DOMContentLoaded", function (){
    render(<Header newSession={newSession} getSession={(faction)=>getSession(last_session_id, faction)} />, document.getElementById("header"));
    if (last_session_id !== null && last_session_id !== undefined){
        getSession(last_session_id, "guild");
    }
});
