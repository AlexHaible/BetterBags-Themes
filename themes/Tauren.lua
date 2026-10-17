local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesTauren",
  DisplayName = "Races - Tauren",
  Description = "A Tauren inspired theme.",
  Background = ns.TEXTURES .. "LightGrassBackground.png",
  BackgroundTileSize = 128,
  BackgroundInset = 8,
  Color = { 0.5, 0.5, 0.5, 0.8 },
  Border = ns.TEXTURES .. "TaurenBorder.png",
  Slice = 32,
  Outset = 32,
  TitleFont = ns.WHITE_OUTLINE,
  TitleY = 32,
  Close = { X = 32, Y = 32 },
  Search = ns.SearchPoints("TOP", 0, 0),
  Menu = { X = -32, Y = 32 },
  Crest = ns.TEXTURES .. "TaurenCrest.png",
  -- Tabs: green weave, the red corner fans.
  TabEdge = { 0.28, 0.33, 0.22, 1 },
  TabAccent = { 0.7, 0.38, 0.28, 1 },
}))
