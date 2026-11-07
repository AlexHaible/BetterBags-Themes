local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesWindshaperSkyborne",
  DisplayName = "Races - Windshaper Skyborne",
  Description = "A Windshaper Skyborne inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.05, 0.08, 0.13, 0.8 },
  Border = ns.TEXTURES .. "WindshaperSkyborneBorder.png",
  Slice = 44,
  Outset = 22,
  TitleY = 40,
  Close = { X = 22, Y = 22 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -26, Y = 26 },
  Crest = ns.TEXTURES .. "WindshaperSkyborneCrest.png",
  -- Tabs: the silver-grey rails, the cerulean enamel.
  TabEdge = { 0.72, 0.76, 0.82, 1 },
  TabAccent = { 0.3, 0.62, 0.86, 1 },
}))
