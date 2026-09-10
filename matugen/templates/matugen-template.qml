import QtQuick

// =============================================================================
// TEMPLATE MATUGEN PER QUICKSHELL
// Copia questo file in ~/.config/matugen/templates/quickshell-theme.qml
// e configuralo in ~/.config/matugen/config.toml
// =============================================================================

QtObject {
    id: theme

    // Palette Generata da Matugen (Material You)
    property color background: "{{colors.surface.dark.hex}}"
    property color surface: "{{colors.surface_container.dark.hex}}"
    property color surfaceVariant: "{{colors.surface_container_high.dark.hex}}"
    property color border: "{{colors.outline_variant.dark.hex}}"
    property color borderActive: "{{colors.primary.dark.hex}}"

    // Colori di Accento
    property color primary: "{{colors.primary.dark.hex}}"
    property color textOnPrimary: "{{colors.on_primary.dark.hex}}"
    property color secondary: "{{colors.secondary.dark.hex}}"
    property color tertiary: "{{colors.tertiary.dark.hex}}"
    property color warning: "{{colors.tertiary.dark.hex}}"
    property color orange: "{{colors.secondary.dark.hex}}"
    property color error: "{{colors.error.dark.hex}}"

    // Testo
    property color text: "{{colors.on_surface.dark.hex}}"
    property color textMuted: "{{colors.on_surface_variant.dark.hex}}"

    // Tipografia
    property string fontMain: "JetBrainsMono Nerd Font, JetBrains Mono, sans-serif"
}
