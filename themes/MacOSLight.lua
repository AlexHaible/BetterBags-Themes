local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.MacOS({
  Name = "MacOSLight",
  DisplayName = "MacOS - Light",
  Description = "A MacOS inspired theme.",
  Art = "MacOSLight",
  Color = { 1, 1, 1, 0.5 },
  Bottom = 5,
  Sides = false,
  -- Tabs like the title bar, edged like the search field, white while selected, with dark text.
  Tab = {
    Fill = { Color = { 0.87, 0.87, 0.87, 0.95 } },
    Edge = { 0.7, 0.7, 0.7, 1 },
    Accent = { 0.45, 0.45, 0.45, 1 },
    EdgeSize = 1,
    TextColor = { 0.35, 0.35, 0.35, 1 },
    BrightTextColor = { 0.1, 0.1, 0.1, 1 },
    Hover = { 0, 0, 0, 0.06 },
    SelectedFill = { 1, 1, 1, 1 },
  },
}))
