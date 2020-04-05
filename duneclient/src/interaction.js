

export function isInteractionInProcess(interaction, type) {
    const selectModes = ["token-select", "space-sector-select", "space-sector-select-start", "space-sector-select-end", "sector-select", "space-select"];
    if (selectModes.indexOf(type) === -1) {
        // This interaction couldn't even be in progress!
        return false;
    }

    if (interaction.mode !== type) {
        return false;
    }

    return true;
};
