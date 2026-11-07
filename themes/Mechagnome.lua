local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "RacesMechagnome",
  DisplayName = "Races - Mechagnome",
  Description = "A Mechagnome inspired theme.",
  Background = ns.SOLID,
  BackgroundInset = 8,
  Color = { 0.02, 0.06, 0.07, 0.8 },
  Border = ns.TEXTURES .. "MechagnomeBorder.png",
  Slice = 48,
  Outset = 20,
  TitleY = 27,
  Close = { X = 16, Y = 16 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  Menu = { X = -28, Y = 28 },
  Crest = ns.TEXTURES .. "MechagnomeCrest.png",
  -- Tabs: teal-patinated bronze, the cyan energy line.
  TabEdge = { 0.16, 0.30, 0.29, 1 },
  TabAccent = { 0.35, 0.88, 0.95, 1 },
}))
