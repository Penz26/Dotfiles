-- In ~/.config/caelestia/hypr-user.lua
hl.bind("SUPER_L", hl.dsp.exec_cmd("echo toggle > /tmp/qs-launcher.fifo"), { release = true })

local vars = require("variables")
local fn = require("utils.functions")

-- Configurazioni Tastiera
hl.config({
	input = {
		kb_layout = "it",
		numlock_by_default = false,
		repeat_delay = 250,
		repeat_rate = 35,
		focus_on_close = 1,

		touchpad = {
			natural_scroll = true,
			disable_while_typing = vars.touchpadDisableTyping,
			scroll_factor = vars.touchpadScrollFactor,
		},
	},

	binds = {
		scroll_event_delay = 0,
	},

	cursor = {
		hotspot_padding = 1,
	},
})

-- Tipo di window management
hl.config({
	general = {
		layout = "scrolling",

		allow_tearing = false, -- Allows `immediate` window rule to work

		gaps_workspaces = vars.workspaceGaps,
		gaps_in = vars.windowGapsIn,
		gaps_out = vars.windowGapsOut,
		border_size = vars.windowBorderSize,

		col = {
			active_border = vars.activeWindowBorderColour,
			inactive_border = vars.inactiveWindowBorderColour,
		},
	},

	dwindle = {
		preserve_split = true,
		smart_split = false,
		smart_resizing = true,
	},

	scrolling = {
		fullscreen_on_one_column = true,
		focus_fit_method = 1,
		column_width = 0.5,
		follow_focus = true,
		follow_min_visible = 0.0,
		explicit_column_widths = "0.35, 0.5, 0.65, 1.0",
	},
})

-- Environment
hl.env("XCURSOR_THEME", "Bibata-Modern-Ice")
hl.env("XCURSOR_SIZE", "20")

-- Settings
hl.config({
	misc = {
		vrr = 1,
	},
})

-- Monitors
hl.monitor({
	output = "HDMI-A-1",
	disabled = false,
	mode = "1920x1080@120.00Hz",
	position = "-290x670",
	scale = 1,
	cm = "srgb",
})
hl.monitor({
	output = "eDP-1",
	disabled = false,
	mode = "1920x1080@60.00Hz",
	position = "-2220x670",
	scale = 1,
	cm = "srgb",
})

-- Special workspaces are already handled natively by Caelestia (configured via cli.json and hypr-vars.lua)

-- Custom app keybinds
if vars.kbNotesApp and vars.notesApp then
	hl.bind(vars.kbNotesApp, hl.dsp.exec_cmd(vars.notesApp))
end
