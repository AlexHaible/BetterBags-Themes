local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesZandalariTroll",
  DisplayName = "Races - Zandalari Troll",
  Description = "A Zandalari Troll inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.02, 0.09, 0.08, 0.75 },
  Border = ns.TEXTURES .. "ZandalariTrollBorder.png",
  Slice = 32,
  Outset = 25,
  TitleFont = ns.WHITE_OUTLINE,
  FlatTitleFont = ns.WHITE_OUTLINE,
  TitleY = 42,
  Close = { X = 24, Y = 24 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -30, Y = 30 },
  Crest = ns.TEXTURES .. "ZandalariTrollCrest.png",
  -- Tabs: temple gold, the jade inlay.
  TabEdge = { 0.72, 0.55, 0.2, 1 },
  TabAccent = { 0.25, 0.75, 0.62, 1 },
}))
