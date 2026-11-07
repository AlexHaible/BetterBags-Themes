local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesLightforgedDraenei",
  DisplayName = "Races - Lightforged Draenei",
  Description = "A Lightforged Draenei inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.07, 0.06, 0.045, 0.8 },
  Border = ns.TEXTURES .. "LightforgedDraeneiBorder.png",
  Slice = 40,
  Outset = 21,
  TitleY = 42,
  Close = { X = 20, Y = 20 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -27, Y = 27 },
  Crest = ns.TEXTURES .. "LightforgedDraeneiCrest.png",
  -- Tabs: the polished gold, the light crystal.
  TabEdge = { 0.78, 0.6, 0.26, 1 },
  TabAccent = { 1, 0.93, 0.6, 1 },
}))
