local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.MacOS({
  Name = "MacOSDark",
  DisplayName = "MacOS - Dark",
  Description = "A MacOS inspired theme.",
  Art = "MacOSDark",
  Color = { 0, 0, 0, 0.75 },
  Bottom = 8,
  Sides = true,
  -- Tabs like the search field: its dark fill and edge, lighter while selected.
  Tab = {
    Fill = { Color = { 0.12, 0.11, 0.13, 0.95 } },
    Edge = { 0.25, 0.25, 0.27, 1 },
    Accent = { 0.6, 0.6, 0.62, 1 },
    EdgeSize = 1,
    TextColor = { 0.75, 0.75, 0.75, 1 },
    Hover = { 1, 1, 1, 0.06 },
  },
}))
