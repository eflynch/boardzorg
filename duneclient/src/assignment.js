import React from 'react';

const ALLOWED_ROLES = ["host", "fremen", "atreides", "guild", "harkonnen", "emperor", "bene-gesserit"];

class Assignment extends React.Component {
    render () {
        let {assignedRoles, assignRole} = this.props;
        const unassignedRoles = ALLOWED_ROLES.filter((r)=>{return assignedRoles.indexOf(r) === -1;});
        const buttons = unassignedRoles.map((r)=>{
            return <button key={r} onClick={(e)=>{assignRole(r);}}>{r}</button>;
        });
        const AssignmentTitle = ({hasRoles}) => {
            if (hasRoles) {
                return <span>Select role to receive secret URL</span>;
            }
            return <span>All roles have been assigned for this game</span>;
        };
        return (
            <div className="main-assignment">
                <AssignmentTitle hasRoles={buttons.length > 0} />
                {buttons}
            </div>
        );
    }
}

module.exports = Assignment;
