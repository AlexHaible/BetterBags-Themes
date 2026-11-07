local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesHaranir",
  DisplayName = "Races - Haranir",
  Description = "A Haranir inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.02, 0.03, 0.09, 0.82 },
  Border = ns.TEXTURES .. "HaranirBorder.png",
  Slice = 40,
  Outset = 22,
  TitleY = 40,
  Close = { X = 22, Y = 22 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -27, Y = 27 },
  Crest = ns.TEXTURES .. "HaranirCrest.png",
  -- Tabs: olive living vine, the glowing blue rune.
  TabEdge = { 0.4, 0.46, 0.22, 1 },
  TabAccent = { 0.4, 0.66, 1.0, 1 },
}))
