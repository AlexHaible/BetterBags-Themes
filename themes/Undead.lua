local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesUndead",
  DisplayName = "Races - Undead",
  Description = "A Undead inspired theme.",
  Background = "Interface\\ChatFrame\\ChatFrameBackground",
  BackgroundTileSize = 128,
  BackgroundInset = 8,
  Color = { 0, 0, 0, 1 },
  Border = ns.TEXTURES .. "UndeadBorder.png",
  Slice = 13,
  Outset = 13,
  TitleY = 0,
  Close = { X = 1, Y = 0 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -24, Y = 24 },
  Crest = ns.TEXTURES .. "UndeadCrest.png",
  CrestScale = 0.35,
}))
