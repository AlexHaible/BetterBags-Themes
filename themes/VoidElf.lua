local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesVoidElf",
  DisplayName = "Races - Void Elf",
  Description = "A Void Elf inspired theme.",
  Background = ns.TEXTURES .. "VoidRockBackground.png",
  BackgroundTileSize = 128,
  BackgroundInset = 8,
  Color = { 0.85, 0.85, 1, 0.8 },
  Border = ns.TEXTURES .. "VoidElfBorder.png",
  Slice = 26,
  Outset = 22,
  TitleY = 26,
  Close = { X = 22, Y = 22 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -28, Y = 28 },
  Crest = ns.TEXTURES .. "VoidElfCrest.png",
  -- Tabs: void black, its purple sparks.
  TabEdge = { 0.09, 0.05, 0.09, 1 },
  TabAccent = { 0.6, 0.35, 0.9, 1 },
}))
