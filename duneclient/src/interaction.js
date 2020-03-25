

export function isInteractionInProcess(interaction, type) {
    const selectModes = ["token-select", "space-sector-select", "sector-select", "space-select"];
    if (selectModes.indexOf(type) !== -1) {
        if (selectModes.indexOf(interaction.mode) !== -1) {
            return interaction.selected === null;
        }
        return true;
    }
    return false;
};
