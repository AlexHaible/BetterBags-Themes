local _, ns = ...

-- BetterBags Next draws its look from a Next theme (BetterBags' .claude/rules/next-themes.md): data only, like the
-- classic bags' Sonata themes, registered with Sonata:RegisterNextTheme and picked on the Appearance page of
-- BetterBags' settings while BetterBags Next is in use. The themes in this folder are the race themes carried over
-- in spirit: their colors and motifs, with art made for a Next bag (tools/next_ornaments.py). A Next bag is a column
-- at the edge of the screen rather than a framed window, so the art is ornaments BetterBags draws on its body (Panel.
-- Ornaments: the roots down its side, a lantern by its title), smaller than the classic borders, and moving.

ns.NEXT_TEXTURES = ns.TEXTURES .. "next\\"

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

-- RegisterNextTheme registers a Next theme with a BetterBags that has Next themes (an older one has none).
---@param theme table
function ns.RegisterNextTheme(theme)
  if sonata.RegisterNextTheme == nil then
    return
  end
  sonata:RegisterNextTheme(theme)
end
