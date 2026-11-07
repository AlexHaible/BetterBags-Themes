local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesDraenei",
  DisplayName = "Races - Draenei",
  Description = "A Draenei inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.05, 0.04, 0.12, 0.78 },
  Border = ns.TEXTURES .. "DraeneiBorder.png",
  Slice = 40,
  Outset = 22,
  TitleY = 40,
  Close = { X = 22, Y = 22 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -27, Y = 27 },
  Crest = ns.TEXTURES .. "DraeneiCrest.png",
  -- Tabs: pearl naaru silver, the amethyst crystal.
  TabEdge = { 0.72, 0.72, 0.8, 1 },
  TabAccent = { 0.62, 0.42, 0.95, 1 },
}))
