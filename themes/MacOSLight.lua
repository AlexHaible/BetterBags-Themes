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
}))
