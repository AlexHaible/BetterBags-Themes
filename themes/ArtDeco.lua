local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

sonata:RegisterTheme(ns.Framed({
  Name = "ThemesArtDeco",
  DisplayName = "Art Deco",
  Description = "An extravagant Art Deco theme.",
  Background = "Interface\\Azerite\\AzeriteTooltipBackground",
  BackgroundInset = 8,
  Color = { 1, 1, 1, 1 },
  Border = ns.TEXTURES .. "ArtDecoBorder.png",
  Slice = 64,
  Outset = 16,
  TitleFont = ns.Font("PoiretOne-Regular.ttf", 12),
  FlatTitleFont = ns.Font("PoiretOne-Regular.ttf", 12),
  BagTitleFont = ns.Font("PoiretOne-Regular.ttf", 24),
  BagTitleHeight = false,
  TitleY = 0,
  Close = { X = 16, Y = 16 },
  Search = ns.SearchPoints("TOPRIGHT", -22, -2),
  -- Blizzard's bag portrait, where BetterBags puts it.
  Menu = { X = -10, Y = 7 },
  -- Tabs: a thin line of the border's pale gold, brighter while selected, in Poiret One.
  TabEdge = { 0.82, 0.74, 0.6, 1 },
  TabAccent = { 0.95, 0.85, 0.6, 1 },
  TabEdgeSize = 1,
  TabFont = ns.Font("PoiretOne-Regular.ttf", 14),
}))
