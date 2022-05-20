import React from 'react';

class Assignment extends React.Component {
    render () {
        let {assignedRoles, unassignedRoles, assignRole} = this.props;
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
