local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesDracthyr",
  DisplayName = "Races - Dracthyr",
  Description = "A Dracthyr inspired theme.",
  Background = ns.SOLID,
  BackgroundTileSize = 128,
  BackgroundInset = 8,
  Color = { 0, 0, 0, 0.75 },
  Border = ns.TEXTURES .. "DracthyrBorder.png",
  Slice = 19,
  Outset = 19,
  TitleFont = ns.WHITE_OUTLINE,
  TitleY = 22,
  Close = { X = 20, Y = 20 },
  Search = ns.SearchPoints("TOP", 0, -4),
  Menu = { X = -24, Y = 24 },
  Crest = ns.TEXTURES .. "DracthyrCrest.png",
  -- Tabs: olive band, its gold key pattern.
  TabEdge = { 0.25, 0.19, 0.08, 1 },
  TabAccent = { 0.66, 0.53, 0.24, 1 },
}))
