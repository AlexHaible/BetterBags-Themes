local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesHighOrderSkyborne",
  DisplayName = "Races - High Order Skyborne",
  Description = "A High Order Skyborne inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.065, 0.06, 0.095, 0.8 },
  Border = ns.TEXTURES .. "HighOrderSkyborneBorder.png",
  Slice = 44,
  Outset = 20,
  TitleY = 40,
  Close = { X = 20, Y = 20 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -22, Y = 22 },
  Crest = ns.TEXTURES .. "HighOrderSkyborneCrest.png",
  -- Tabs: ivory marble, the arcane violet.
  TabEdge = { 0.8, 0.76, 0.68, 1 },
  TabAccent = { 0.72, 0.5, 1.0, 1 },
}))
