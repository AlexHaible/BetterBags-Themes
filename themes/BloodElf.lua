local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesBloodElf",
  DisplayName = "Races - Blood Elf",
  Description = "A Blood Elf inspired theme.",
  Background = ns.TEXTURES .. "MarbleBackground.png",
  BackgroundTileSize = 128,
  BackgroundInset = 8,
  FlatBackgroundInset = 16,
  Color = { 1, 0.85, 0.85, 1 },
  PanelColor = { 0.8, 0.65, 0.65, 0.9 },
  Border = ns.TEXTURES .. "BloodElfBorderNew.png",
  Slice = 24,
  Outset = 24,
  TitleY = 28,
  Close = { X = 24, Y = 24 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -32, Y = 32 },
  Crest = ns.TEXTURES .. "BloodElfCrest.png",
  -- Tabs: gold trim, the corner gems' green.
  TabEdge = { 0.68, 0.56, 0.3, 1 },
  TabAccent = { 0.35, 0.8, 0.25, 1 },
}))
