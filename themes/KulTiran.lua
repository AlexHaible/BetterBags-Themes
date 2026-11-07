local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesKulTiran",
  DisplayName = "Races - Kul Tiran",
  Description = "A Kul Tiran inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.02, 0.06, 0.065, 0.82 },
  Border = ns.TEXTURES .. "KulTiranBorder.png",
  Slice = 48,
  Outset = 22,
  TitleY = 28,
  Close = { X = 18, Y = 18 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -28, Y = 28 },
  Crest = ns.TEXTURES .. "KulTiranCrest.png",
  -- Tabs: teak planking, the brass fittings.
  TabEdge = { 0.28, 0.16, 0.08, 1 },
  TabAccent = { 0.82, 0.62, 0.24, 1 },
}))
