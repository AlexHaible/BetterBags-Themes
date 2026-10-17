local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesNightElf",
  DisplayName = "Races - Night Elf",
  Description = "A Night Elf inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.01, 0.2, 0.01, 0.7 },
  Border = ns.TEXTURES .. "NightElfBorder.png",
  Slice = 74,
  Outset = 24,
  TitleY = 20,
  Close = { X = 16, Y = 16 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -22, Y = 28 },
  Crest = ns.TEXTURES .. "NightElfCrest.png",
  CrestScale = 0.35,
  -- Tabs: bark, the leaves' green.
  TabEdge = { 0.07, 0.06, 0.06, 1 },
  TabAccent = { 0.45, 0.75, 0.2, 1 },
  -- The bark beam along the bottom stops 5 short of the border's edge.
  ArtBelow = 19,
}))
