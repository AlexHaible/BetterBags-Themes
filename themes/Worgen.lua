local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesWorgen",
  DisplayName = "Races - Worgen",
  Description = "A Worgen inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.05, 0.055, 0.065, 0.8 },
  Border = ns.TEXTURES .. "WorgenBorder.png",
  Slice = 48,
  Outset = 22,
  TitleY = 24,
  Close = { X = 18, Y = 18 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -28, Y = 28 },
  Crest = ns.TEXTURES .. "WorgenCrest.png",
  -- Tabs: wrought iron, the crimson rose.
  TabEdge = { 0.24, 0.25, 0.28, 1 },
  TabAccent = { 0.55, 0.1, 0.12, 1 },
}))
