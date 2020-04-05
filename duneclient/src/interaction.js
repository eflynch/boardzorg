

export function isInteractionInProcess(interaction, type) {
    const selectModes = ["token-select", "space-sector-select", "space-sector-select-start", "space-sector-select-end", "sector-select", "space-select"];
    if (selectModes.indexOf(type) !== -1) {
        if (selectModes.indexOf(interaction.mode) !== -1) {
            return interaction[interaction.mode] === null;
        }
        return true;
    }
    return false;
};
