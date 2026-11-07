local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesEarthen",
  DisplayName = "Races - Earthen",
  Description = "An Earthen inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.06, 0.07, 0.09, 0.8 },
  Border = ns.TEXTURES .. "EarthenBorder.png",
  Slice = 44,
  Outset = 22,
  TitleY = 40,
  Close = { X = 22, Y = 22 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -26, Y = 26 },
  Crest = ns.TEXTURES .. "EarthenCrest.png",
  -- Tabs: titan stone, the gold trim.
  TabEdge = { 0.5, 0.55, 0.62, 1 },
  TabAccent = { 0.85, 0.66, 0.28, 1 },
}))
