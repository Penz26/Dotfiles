-- Generato automaticamente da Matugen
local M = {}

M.colors = {
	bg = "{{colors.surface.default.hex}}",
	fg = "{{colors.on_surface.default.hex}}",
	accent = "{{colors.primary.default.hex}}",
	on_accent = "{{colors.on_primary.default.hex}}",
	surface_alt = "{{colors.surface_container_high.default.hex}}",
	comment = "{{colors.outline.default.hex}}",
	error = "{{colors.error.default.hex}}",
	string = "{{colors.tertiary.default.hex}}",
}

function M.setup()
	vim.cmd("highlight clear")
	if vim.fn.exists("syntax_on") == 1 then
		vim.cmd("syntax reset")
	end

	vim.o.termguicolors = true
	vim.g.colors_name = "matugen"

	local hl = vim.api.nvim_set_hl

	-- Highlight Groups principali
	hl(0, "Normal", { fg = M.colors.fg, bg = "NONE" }) -- bg = "NONE" per mantenere la trasparenza di Kitty
	hl(0, "NormalFloat", { fg = M.colors.fg, bg = M.colors.surface_alt })
	hl(0, "FloatBorder", { fg = M.colors.accent, bg = "NONE" })
	hl(0, "CursorLine", { bg = M.colors.surface_alt })
	hl(0, "LineNr", { fg = M.colors.comment })
	hl(0, "CursorLineNr", { fg = M.colors.accent, bold = true })

	-- Sintassi base
	hl(0, "Keyword", { fg = M.colors.accent, bold = true })
	hl(0, "Function", { fg = M.colors.accent })
	hl(0, "String", { fg = M.colors.string })
	hl(0, "Comment", { fg = M.colors.comment, italic = true })
	hl(0, "Error", { fg = M.colors.error })
	hl(0, "Visual", { bg = M.colors.surface_alt })
end

return M
