local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesHighmountainTauren",
  DisplayName = "Races - Highmountain Tauren",
  Description = "A Highmountain Tauren inspired theme.",
  Background = ns.TEXTURES .. "LightGrassBackground.png",
  BackgroundTileSize = 128,
  BackgroundInset = 8,
  Color = { 0.3764705882352941, 0.5019607843137255, 0.24705882352941178, 0.75 },
  Border = ns.TEXTURES .. "HighmountainTaurenBorder.png",
  Slice = 32,
  Outset = 32,
  TitleFont = ns.WHITE_OUTLINE,
  TitleY = 32,
  Close = { X = 32, Y = 32 },
  Search = ns.SearchPoints("TOP", 0, 0),
  Menu = { X = -32, Y = 32 },
  Crest = ns.TEXTURES .. "HighmountainTaurenCrest.png",
  -- Tabs: red-brown braids, the tan corner blocks.
  TabEdge = { 0.38, 0.23, 0.2, 1 },
  TabAccent = { 0.86, 0.76, 0.55, 1 },
}))
