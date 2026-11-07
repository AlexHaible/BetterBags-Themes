local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesGoblin",
  DisplayName = "Races - Goblin",
  Description = "A Goblin inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.05, 0.08, 0.05, 0.8 },
  Border = ns.TEXTURES .. "GoblinBorder.png",
  Slice = 48,
  Outset = 24,
  TitleY = 29,
  Close = { X = 18, Y = 18 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -28, Y = 28 },
  Crest = ns.TEXTURES .. "GoblinCrest.png",
  -- Tabs: gunmetal, the green glass.
  TabEdge = { 0.25, 0.27, 0.27, 1 },
  TabAccent = { 0.55, 0.85, 0.2, 1 },
}))
