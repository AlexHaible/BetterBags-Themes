local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

-- A flower and a rune circle at each corner of the bag, 64 by 64, centered 16 outside it.
-- The top left flower draws above its rune circle; at the other corners the rune circle draws
-- above the flower.
---@param name string
---@param file string
---@param point string
---@param x number
---@param y number
---@param layer DrawLayer
---@param subLevel number
---@return table
local function corner(name, file, point, x, y, layer, subLevel)
  return {
    Name = name,
    Texture = ns.TEXTURES .. file,
    Layer = layer,
    SubLevel = subLevel,
    Points = { { Point = point, X = x, Y = y } },
    Size = { Width = 64, Height = 64 },
    Opacity = true,
  }
end

sonata:RegisterTheme(ns.Framed({
  Name = "RacesNightborne",
  DisplayName = "Races - Nightborne",
  Description = "A Nightborne inspired theme.",
  Background = ns.TEXTURES .. "SuramarGrassBackground.png",
  BackgroundTileSize = 256,
  BackgroundInset = 32,
  Color = { 1, 1, 1, 1 },
  Border = ns.TEXTURES .. "NightborneBorder.png",
  Slice = 32,
  Outset = 32,
  TitleFont = ns.WHITE_OUTLINE,
  FlatTitleFont = ns.WHITE_OUTLINE,
  TitleY = 30,
  Close = { X = 28, Y = 28 },
  Search = ns.SearchPoints("TOP", 0, -8),
  Menu = { X = -32, Y = 32 },
  Crest = ns.TEXTURES .. "NightborneCrest.png",
  BagTextures = {
    corner("Flower1", "NightborneFlower.png", "TOPLEFT", -48, 48, "OVERLAY", 2),
    corner("Flower2", "NightborneFlower.png", "TOPRIGHT", 48, 48, "ARTWORK", 0),
    corner("Flower3", "NightborneFlower.png", "BOTTOMLEFT", -48, -48, "ARTWORK", 0),
    corner("Flower4", "NightborneFlower.png", "BOTTOMRIGHT", 48, -48, "ARTWORK", 0),
    corner("RuneCircle1", "NightborneRuneCircle.png", "TOPLEFT", -48, 48, "ARTWORK", 1),
    corner("RuneCircle2", "NightborneRuneCircle.png", "TOPRIGHT", 48, 48, "ARTWORK", 1),
    corner("RuneCircle3", "NightborneRuneCircle.png", "BOTTOMLEFT", -48, -48, "ARTWORK", 1),
    corner("RuneCircle4", "NightborneRuneCircle.png", "BOTTOMRIGHT", 48, -48, "ARTWORK", 1),
  },
}))
