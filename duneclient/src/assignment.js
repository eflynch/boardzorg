import React from 'react';

const ALLOWED_ROLES = ["host", "fremen", "atreides", "guild", "harkonnen", "emperor", "bene-gesserit"];

class Assignment extends React.Component {
    render () {
        let {assignedRoles, assignRole} = this.props;
        const unassignedRoles = ALLOWED_ROLES.filter((r)=>{return assignedRoles.indexOf(r) === -1;});
        const buttons = unassignedRoles.map((r)=>{
            return <button key={r} onClick={(e)=>{assignRole(r);}}>{r}</button>;
        });
        return (
            <div className="main-assignment">
                {assignedRoles}
                {buttons}
            </div>
        );
    }
}

module.exports = Assignment;
