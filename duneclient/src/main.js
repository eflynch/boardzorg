import React from 'react';
import $ from 'jquery';
import {render} from 'react-dom';

import Header from './header'
import Session from './session'
import Assignment from './assignment'
import SessionCreator from './session-creator'

var last_data;
var last_assignment_data;


function renderSession(sessionID, roleID, data, error){
    if (sessionID === null || sessionID === undefined){
        return;
    }
    last_data = data;
    let {state, actions, history, role} = data;
    render(<Session me={role} state={state} actions={actions} history={history} error={error} sendCommand={function(cmd){
        sendCommand(sessionID, roleID, cmd);
    }}/>, document.getElementById("content"));
}

function renderAssignment(sessionID, data, error) {
    last_assignment_data = data;
    render(<Assignment assignedRoles={data.assigned_roles} assignRole={(role)=>{
        assignRole(sessionID, role);}} />, document.getElementById("content"));
}

function getAssignedRoles(sessionID) {
    $.getJSON(`/api/sessions/${sessionID}/roles`, function(data){
        renderAssignment(sessionID, data);
    })
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
    $.getJSON("/api/sessions/" + sessionID, {role_id: roleID}, function(data){
        document.title = `Shai-Hulud: ${data.role}`;
        renderSession(sessionID, roleID, data);
    });
}

function newSession(name){
    $.ajax({
        type: "POST",
        url: "/api/sessions",
        data: JSON.stringify({session_id: name}),
        success: function(data){
            window.location = "/" + data.id;
        },
        error: function(data){
        },
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
}

function renderNewSessions() {
    render(<SessionCreator newSession={newSession} />, document.getElementById("content"));
}

document.addEventListener("DOMContentLoaded", function (){
    const sessionID= window.bootstrap.sessionID;
    const roleID= window.bootstrap.roleID;
    render(<Header sessionTitle={sessionID} />, document.getElementById("header"));
    if (sessionID === null || sessionID === undefined) {
        renderNewSessions();
    } else if (roleID === null || roleID === undefined) {
        getAssignedRoles(sessionID);
        setInterval(()=>{
            getAssignedRoles(sessionID);
        }, 1000);
    } else{
        getSession(sessionID, roleID);
        setInterval(()=>{
            getSession(sessionID, roleID);
        }, 1000);
    }
});
