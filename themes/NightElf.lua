local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesNightElf",
  DisplayName = "Races - Night Elf",
  Description = "A Night Elf inspired theme.",
  Background = "Interface\\ChatFrame\\ChatFrameBackground",
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
}))
