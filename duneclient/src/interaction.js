

export function isInteractionInProcess(interaction, type) {
    if (type === "token-select") {
        if (interaction.mode === "token-select") {
            return interaction.selected === null;
        }
        return true;
    }
    return false;
};
