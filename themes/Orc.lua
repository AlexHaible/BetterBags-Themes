local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesOrc",
  DisplayName = "Races - Orc",
  Description = "A Orc inspired theme.",
  Background = "Interface\\ChatFrame\\ChatFrameBackground",
  BackgroundInset = 8,
  Color = { 0.2, 0.01, 0.01, 0.7 },
  Border = ns.TEXTURES .. "OrcBorder.png",
  Slice = 74,
  Outset = 24,
  TitleY = 20,
  Close = { X = 16, Y = 16 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -24, Y = 24 },
  Crest = ns.TEXTURES .. "OrcCrest.png",
}))
