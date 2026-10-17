local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesPandaren",
  DisplayName = "Races - Pandaren",
  Description = "A Pandaren inspired theme.",
  Background = "Interface\\ChatFrame\\ChatFrameBackground",
  BackgroundTileSize = 128,
  BackgroundInset = 20,
  Color = { 0.01, 0.2, 0.01, 0.7 },
  Border = ns.TEXTURES .. "PandarenBorder.png",
  Slice = 32,
  Outset = 32,
  TitleFont = ns.WHITE_OUTLINE,
  FlatTitleFont = ns.WHITE_OUTLINE,
  TitleY = 38,
  Close = { X = 32, Y = 32 },
  Search = ns.SearchPoints("TOP", 0, 8),
  Menu = { X = -32, Y = 32 },
  Crest = ns.TEXTURES .. "PandarenCrest.png",
}))
