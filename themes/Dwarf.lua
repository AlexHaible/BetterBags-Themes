local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesDwarf",
  DisplayName = "Races - Dwarf",
  Description = "A Dwarf inspired theme.",
  Background = ns.TEXTURES .. "MarbleBackground.png",
  BackgroundTileSize = 128,
  BackgroundInset = 8,
  Color = { 0.85, 0.85, 1, 1 },
  Border = ns.TEXTURES .. "DwarfBorder.png",
  Slice = 52,
  Outset = 48,
  TitleY = 40,
  Close = { X = 36, Y = 36 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -42, Y = 42 },
  Crest = ns.TEXTURES .. "DwarfCrest.png",
  -- Tabs: stone, the bronze braids.
  TabEdge = { 0.38, 0.36, 0.36, 1 },
  TabAccent = { 0.72, 0.45, 0.2, 1 },
}))
