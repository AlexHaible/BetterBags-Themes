local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesVulpera",
  DisplayName = "Races - Vulpera",
  Description = "A Vulpera inspired theme.",
  Background = ns.TEXTURES .. "SandDuneBackground.png",
  BackgroundTileSize = 128,
  BackgroundInset = 12,
  Color = { 0.6470588235294118, 0.5568627450980392, 0.35294117647058826, 1 },
  Border = ns.TEXTURES .. "VulperaBorder.png",
  Slice = 30,
  Outset = 30,
  TitleFont = ns.WHITE_OUTLINE,
  TitleY = 32,
  Close = { X = 28, Y = 28 },
  Search = ns.SearchPoints("TOP", 0, 0),
  Menu = { X = -32, Y = 32 },
  Crest = ns.TEXTURES .. "VulperaCrest.png",
}))
