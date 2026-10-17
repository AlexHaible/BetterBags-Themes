local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesMagharOrc",
  DisplayName = "Races - Mag'har Orc",
  Description = "A Mag'har Orc inspired theme.",
  Background = ns.TEXTURES .. "MagharOrcBackground.png",
  BackgroundTileSize = 128,
  BackgroundInset = 8,
  Color = { 1, 0.85, 0.85, 1 },
  Border = ns.TEXTURES .. "MagharOrcBorder.png",
  Slice = 32,
  Outset = 32,
  TitleFont = ns.WHITE_OUTLINE,
  TitleY = 32,
  Close = { X = 32, Y = 32 },
  Search = ns.SearchPoints("TOP", 0, 0),
  Menu = { X = -32, Y = 32 },
  Crest = ns.TEXTURES .. "MagharOrcCrest.png",
}))
