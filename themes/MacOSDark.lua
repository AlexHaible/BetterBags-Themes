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
}))
