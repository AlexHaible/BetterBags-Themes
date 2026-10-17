local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesHuman",
  DisplayName = "Races - Human",
  Description = "A Human inspired theme.",
  Background = "Interface\\ChatFrame\\ChatFrameBackground",
  BackgroundInset = 8,
  Color = { 0.01, 0.01, 0.2, 0.7 },
  Border = ns.TEXTURES .. "HumanBorder.png",
  Slice = 54,
  Outset = 16,
  TitleY = 24,
  Close = { X = 16, Y = 16 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -24, Y = 24 },
  Crest = ns.TEXTURES .. "HumanCrest.png",
}))
