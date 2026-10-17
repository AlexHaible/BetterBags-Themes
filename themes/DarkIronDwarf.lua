local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesDarkIronDwarf",
  DisplayName = "Races - Dark Iron Dwarf",
  Description = "A Race inspired theme.",
  Background = ns.TEXTURES .. "MarbleBackground.png",
  BackgroundTileSize = 128,
  BackgroundInset = 8,
  Color = { 1, 0.7, 0.7, 1 },
  Border = ns.TEXTURES .. "DarkIronDwarfBorder.png",
  Slice = 64,
  Outset = 56,
  TitleY = 48,
  Close = { X = 39, Y = 39 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -44, Y = 36 },
  Crest = ns.TEXTURES .. "DarkIronDwarfCrest.png",
  CrestScale = 0.35,
}))
