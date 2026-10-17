local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

local BLUE = { 0.5568627450980392, 0.6980392156862745, 0.8588235294117647, 0.5 }

---@param top? number How far the fill starts below the window's top.
---@return table
local function backdrop(top)
  return {
    BgFile = "Interface\\ChatFrame\\ChatFrameBackground",
    Tile = true,
    TileSize = 128,
    Insets = { Left = 0, Right = 0, Top = top or 0, Bottom = 0 },
    Color = BLUE,
  }
end

-- The glass sheen over the fill, and the window border with its tall title bar, which reaches
-- 20 above the window and 8 to its sides and below it.
---@param top number[] The sheen's TOP point, { x, y }.
---@return table[]
local function textures(top)
  return {
    {
      Name = "Glass",
      Texture = ns.TEXTURES .. "AeroGlassTexture.png",
      Layer = "BORDER",
      VertexColor = { 1, 1, 1, 0.2 },
      Points = {
        { Point = "TOP", X = top[1], Y = top[2] },
        { Point = "RIGHT", X = 8, Y = -8 },
        { Point = "BOTTOM", X = 8, Y = -8 },
        { Point = "LEFT", X = -8, Y = 8 },
      },
      Opacity = true,
    },
    {
      Name = "Border",
      Texture = ns.TEXTURES .. "AeroGlassBorder.png",
      SliceMargins = { Left = 8, Top = 29, Right = 8, Bottom = 8 },
      SliceMode = "Tiled",
      Points = {
        { Point = "TOP", Y = 20 },
        { Point = "RIGHT", X = 8 },
        { Point = "BOTTOM", Y = -8 },
        { Point = "LEFT", X = -8 },
      },
      Opacity = true,
    },
  }
end

local FONT = ns.Font("SegoeUI.ttf", 12)
local TITLE = { Font = FONT, Points = { { Point = "TOPLEFT", X = 4, Y = 20 } }, Height = 30 }

local CLOSE = {
  Size = { Width = 50, Height = 21 },
  Points = { { Point = "TOPRIGHT", Y = 20 } },
  Normal = { Texture = ns.TEXTURES .. "AeroGlassCloseButton.png" },
  Highlight = { Texture = ns.TEXTURES .. "AeroGlassCloseButtonHover.png" },
  Pushed = { Texture = ns.TEXTURES .. "AeroGlassCloseButtonPush.png" },
}

local FLAT = {
  Template = false,
  Backdrop = backdrop(),
  Textures = textures({ -8, -8 }),
  Title = TITLE,
}

local SLOTS = {}
for k, v in pairs(FLAT) do
  SLOTS[k] = v
end
SLOTS.Layout = { Points = { { Point = "BOTTOMLEFT", RelativePoint = "TOPLEFT" } } }

sonata:RegisterTheme({
  Name = "WinAeroGlass",
  DisplayName = "Aero Glass",
  Description = "A Windows 7 inspired theme.",
  Parent = "Default",
  Windows = {
    Bag = {
      Template = false,
      Backdrop = backdrop(8),
      Textures = textures({ 0, 0 }),
      Title = {
        Font = ns.Font("SegoeUI.ttf", 14, "OUTLINE"),
        Points = { { Point = "TOPLEFT", Y = 20 } },
        Height = 30,
      },
      CloseButton = CLOSE,
      Layout = {
        Search = { Points = ns.SearchPoints("TOP", 0, -15), Reserve = 0 },
        -- Left of the close button.
        MenuButton = { Points = { { Point = "TOPRIGHT", X = -49, Y = 20 } } },
      },
    },
    Panel = {
      Template = false,
      Backdrop = backdrop(),
      Textures = textures({ -8, -8 }),
      Title = TITLE,
      CloseButton = CLOSE,
    },
    Dialog = FLAT,
    Slots = SLOTS,
  },
  Elements = {
    SectionHeader = { Font = FONT },
    BagButton = {
      Width = 30,
      Height = 21,
      Portrait = false,
      Highlight = false,
      States = {
        Normal = { Texture = ns.TEXTURES .. "AeroGlassMenuButton.png" },
        Highlight = { Texture = ns.TEXTURES .. "AeroGlassMenuButtonHover.png" },
        Pushed = { Texture = ns.TEXTURES .. "AeroGlassMenuButtonPush.png" },
      },
    },
  },
})
