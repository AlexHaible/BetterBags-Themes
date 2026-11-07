local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesGnome",
  DisplayName = "Races - Gnome",
  Description = "A Gnome inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.04, 0.06, 0.1, 0.8 },
  Border = ns.TEXTURES .. "GnomeBorder.png",
  Slice = 48,
  Outset = 20,
  TitleY = 40,
  Close = { X = 16, Y = 16 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -28, Y = 28 },
  Crest = ns.TEXTURES .. "GnomeCrest.png",
  -- Tabs: polished brass, the cyan crystal.
  TabEdge = { 0.78, 0.58, 0.26, 1 },
  TabAccent = { 0.45, 0.88, 1, 1 },
}))
