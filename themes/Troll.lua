local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesTroll",
  DisplayName = "Races - Troll",
  Description = "A Troll inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.02, 0.12, 0.12, 0.72 },
  Border = ns.TEXTURES .. "TrollBorder.png",
  Slice = 48,
  Outset = 24,
  TitleY = 24,
  Close = { X = 22, Y = 22 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -24, Y = 24 },
  Crest = ns.TEXTURES .. "TrollCrest.png",
  -- Tabs: driftwood, the teal leather lashings.
  TabEdge = { 0.33, 0.26, 0.19, 1 },
  TabAccent = { 0.2, 0.6, 0.56, 1 },
}))
