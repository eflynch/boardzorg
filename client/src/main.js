import React from 'react';
import $ from 'jquery';
import {render} from 'react-dom';
import io from 'socket.io-client';

import Header from './header'
import Session from './session'
import Assignment from './assignment'
import SessionCreator from './session-creator'

var last_data;
var last_assignment_data;


function newSession(name, factions){
    $.ajax({
        type: "POST",
        url: "/api/sessions",
        data: JSON.stringify({session_id: name, factions: factions}),
        success: function(data){
            window.location = "/" + data.id;
        },
        error: function(data){
        },
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
}


function assignRole(sessionID, role) {
    $.ajax({
        type: "POST",
        url: `/api/sessions/${sessionID}/roles`,
        data: JSON.stringify({role: role}),
        success: function(data){
            const roleID = data.role_id;
            window.location = `/${sessionID}/${roleID}`
        },
        error: function(data){
            renderAssignment(sessionID, last_assignment_data, data.responseJSON);
        },
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    }); 
}


function renderSession(sessionID, roleID, data, error){
    if (sessionID === null || sessionID === undefined){
        return;
    }
    last_data = data;
    let {state, actions, history, role} = data;
    const actionSetIsBlocking = actions.filter((action)=>action.blocking).length > 0;
    document.getElementById("wrapper").className = actionSetIsBlocking ? "blocking" : "";
    render(<Header sessionTitle={sessionID} role={role} />, document.getElementById("header"));
    render(<Session me={role} state={state} actions={actions} history={history} error={error} sendCommand={function(cmd){
        sendCommand(sessionID, roleID, cmd);
    }}/>, document.getElementById("content"));
}


function renderAssignment(sessionID, data, error) {
    last_assignment_data = data;
    render(<Assignment assignedRoles={data.assigned_roles} unassignedRoles={data.unassigned_roles} assignRole={(role)=>{
        assignRole(sessionID, role);}} />, document.getElementById("content"));
}


function renderNewSessions() {
    render(<SessionCreator newSession={newSession} />, document.getElementById("content"));
}


function sendCommand(sessionID, roleID, cmd){
    $.ajax({
        type: "POST",
        url: "/api/sessions/" + sessionID,
        data: JSON.stringify({role_id: roleID, cmd: cmd}),
        success: function(data){
            renderSession(sessionID, roleID, data, null);
        },
        error: function(data){
            renderSession(sessionID, roleID, last_data, data.responseJSON);
        },
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
}

function getSession(sessionID, roleID){
    const socket = io("/sessions");
    socket.on('connect', () =>{
        socket.emit('join', {
            "session_id": sessionID,
            "role_id": roleID,
        });
    });
    socket.on('sessions', (data) => {
        document.title = `Heffalump: ${data.role}`;
        renderSession(sessionID, roleID, data);
    });
    socket.on('error', () => {
        document.getElementById("content").innerHTML = `${sessionID} does not exist :(`;
    });
    document.getElementById("content").innerHTML = "Loading...";
}

function getAssignedRoles(sessionID) {
    const socket = io("/roles");
    socket.on('connect', () =>{
        socket.emit('join', {
            "session_id": sessionID,
        });
    });
    socket.on('roles', (roles) => {
        renderAssignment(sessionID, roles);
    });
    socket.on('error', () => {
        document.getElementById("content").innerHTML = `${sessionID} does not exist :(`;
    });
    document.getElementById("content").innerHTML = "Loading...";
}



document.addEventListener("DOMContentLoaded", function (){
    const sessionID= window.bootstrap.sessionID;
    const roleID= window.bootstrap.roleID;
    render(<Header sessionTitle={sessionID} role={""} />, document.getElementById("header"));
    if (sessionID === null || sessionID === undefined) {
        renderNewSessions();
    } else if (roleID === null || roleID === undefined) {
        getAssignedRoles(sessionID);
    } else{
        getSession(sessionID, roleID);
    }
});
