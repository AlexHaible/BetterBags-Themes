local _, ns = ...

-- BetterBags draws its windows through Sonata, a declarative theme engine: a theme is a table
-- of window and element styles that BetterBags applies to its own frames (see BetterBags'
-- sonata/README.md). The builders here return such tables; each theme file registers one.
-- A theme inherits whatever it does not set from its Parent: these themes inherit BetterBags'
-- Default, which keeps Blizzard's look on the windows they never styled (the debug window and
-- the search panel the search keybinding opens).

ns.TEXTURES = "Interface\\AddOns\\BetterBags-Themes\\textures\\"
ns.FONTS = "Interface\\AddOns\\BetterBags-Themes\\fonts\\"

-- Fonts. BetterBags' UnitFrame12White (UNIT_NAME_FONT, 12, white, no shadow) is the base of
-- every font here: a font file given after it replaces only the face, size and outline.
ns.WHITE = { Object = "UnitFrame12White" }
ns.WHITE_OUTLINE = { Object = "UnitFrame12White", Path = UNIT_NAME_FONT, Size = 12, Flags = "OUTLINE" }

---@param file string A font file in this addon's fonts folder.
---@param size number
---@param flags? string
---@return table
function ns.Font(file, size, flags)
  return { Object = "UnitFrame12White", Path = ns.FONTS .. file, Size = size, Flags = flags or "" }
end

---@param n number
---@return table
local function around(n)
  return { Left = n, Right = n, Top = n, Bottom = n }
end

-- The search box is 150 by 20, anchored by one corner or edge of the window.
---@param point "TOPRIGHT"|"TOP"
---@param x number
---@param y number
---@return table
function ns.SearchPoints(point, x, y)
  local left = point == "TOP" and x - 75 or x - 150
  local right = point == "TOP" and x + 75 or x
  return {
    { Point = "TOPLEFT", RelativePoint = point, X = left, Y = y },
    { Point = "BOTTOMRIGHT", RelativePoint = point, X = right, Y = y - 20 },
  }
end

-- The Show Bags and bank tab panels sit on top of their bag.
local ABOVE_THE_BAG = { Points = { { Point = "BOTTOMLEFT", RelativePoint = "TOPLEFT" } } }

-- A plain white fill BetterBags tints, as the race themes' solid fills are.
ns.SOLID = "Interface\\ChatFrame\\ChatFrameBackground"

---@param font table
---@param color number[]
---@return table
local function withColor(font, color)
  local copy = {}
  for k, v in pairs(font) do
    copy[k] = v
  end
  copy.Color = color
  return copy
end

---@class TabOptions
---@field Fill table The tab's fill: a texture spec.
---@field Edge number[] The edge's color.
---@field Accent number[] The edge's color while the tab is selected.
---@field EdgeSize? number The edge's width (2 when unset).
---@field Font table The tab text's font.
---@field TextColor? number[] The text's color (light gray when unset).
---@field BrightTextColor? number[] The text's color while hovered or selected (white when unset).
---@field Hover? number[] The overlay while hovered.
---@field SelectedFill? number[] The overlay while selected.

-- Tab builds a flat tab: a fill with an edge around it, the edge in an accent color and the fill
-- lighter while selected. Its art starts 2 into the tab: the tab bar hangs 2 under the art above
-- it (Layout.Tabs).
---@param o TabOptions
---@return table
function ns.Tab(o)
  local inset = { Left = 0, Right = 0, Top = 2, Bottom = 0 }
  local fill = {}
  for k, v in pairs(o.Fill) do
    fill[k] = v
  end
  fill.Inset = inset
  local bright = withColor(o.Font, o.BrightTextColor or { 1, 1, 1, 1 })
  return {
    Art = "Flat",
    Height = 26,
    Background = fill,
    Border = { Color = o.Edge, EdgeSize = o.EdgeSize or 2, Inset = inset },
    Hover = { Color = o.Hover or { 1, 1, 1, 0.08 }, Inset = inset },
    Selected = {
      Background = { Color = o.SelectedFill or { 1, 1, 1, 0.12 }, Inset = inset },
      Border = { Color = o.Accent },
    },
    Font = withColor(o.Font, o.TextColor or { 0.8, 0.8, 0.8, 1 }),
    HighlightFont = bright,
    SelectedFont = bright,
    TextOffset = { X = 0, Y = -1 },
    SelectedTextOffset = { X = 0, Y = -1 },
  }
end

-- TabsBelow hangs the tab bar so its tabs start just under art reaching `below` under the window.
---@param below number
---@param x? number
---@return table
function ns.TabsBelow(below, x)
  return { Offset = { X = x or 0, Y = 2 - below } }
end

---@class FramedThemeOptions
---@field Name string The key the theme is saved under.
---@field DisplayName string
---@field Description string
---@field Background string The backdrop's fill file.
---@field BackgroundInset number How far the fill reaches outside the window.
---@field FlatBackgroundInset? number The same on flat windows (BackgroundInset when unset).
---@field BackgroundTileSize? number Tiles the fill at this size.
---@field Color number[] The fill's tint.
---@field PanelColor? number[] The tint on panels (Color when unset).
---@field Border string The nine-sliced border file.
---@field Slice number The border art's slice margin on each side.
---@field Outset number How far the border reaches outside the window.
---@field TitleFont? table The bag's and panels' title font (white UnitFrame12White when unset).
---@field FlatTitleFont? table The flat windows' title font (white UnitFrame12White when unset).
---@field TitleY number The bag title's offset above the window's top.
---@field BagTitleHeight? number|false The bag title's height (30 when unset; false leaves it to the text).
---@field BagTitleFont? table The bag's title font (TitleFont when unset).
---@field Close {X: number, Y: number} The bag's close button, from the window's top right.
---@field Search table The search box's points (ns.SearchPoints).
---@field Menu {X: number, Y: number} The menu button, from the window's top left.
---@field Crest? string The menu button's art, drawn 275 by 350 at CrestScale (Blizzard's when unset).
---@field CrestScale? number
---@field BagTextures? table[] More art for the bag, drawn after the border.
---@field TabEdge number[] The tabs' edge: the border art's main color.
---@field TabAccent number[] The selected tab's edge: the border art's accent.
---@field TabEdgeSize? number
---@field TabFont? table The tab text's font (white outlined UnitFrame12White when unset).
---@field ArtBelow? number How far the border's art reaches under the window (Outset when unset).
---@field TabsX? number Moves the tabs right, past art at the window's bottom left corner.

-- Framed builds the theme every race theme and Art Deco share: a fill reaching outside the
-- window, a nine-sliced border around it, a title above it, Blizzard's close button, and the
-- race's crest as the menu button.
---@param o FramedThemeOptions
---@return table
function ns.Framed(o)
  local function backdrop(color, inset)
    return {
      BgFile = o.Background,
      Tile = o.BackgroundTileSize ~= nil,
      TileSize = o.BackgroundTileSize,
      Insets = around(-inset),
      Color = color,
    }
  end
  local border = {
    Name = "Border",
    Texture = o.Border,
    Layer = "BORDER",
    SliceMargins = around(o.Slice),
    SliceMode = "Tiled",
    Inset = around(-o.Outset),
    Opacity = true,
  }
  local bagTextures = { border }
  for _, texture in ipairs(o.BagTextures or {}) do
    table.insert(bagTextures, texture)
  end
  local titleFont = o.TitleFont or ns.WHITE
  local flatTitleFont = o.FlatTitleFont or ns.WHITE
  local bagTitle = { Font = o.BagTitleFont or titleFont, Points = { { Point = "TOP", Y = o.TitleY } } }
  if o.BagTitleHeight ~= false then
    bagTitle.Height = o.BagTitleHeight or 30
  end

  local flat = {
    Template = false,
    Backdrop = backdrop(o.Color, o.FlatBackgroundInset or o.BackgroundInset),
    Textures = { border },
    Title = { Font = flatTitleFont, Points = { { Point = "TOP" } }, Height = 30 },
  }
  local slots = {}
  for k, v in pairs(flat) do
    slots[k] = v
  end
  slots.Layout = ABOVE_THE_BAG

  -- The tabs are filled like the window and edged in the border's colors.
  local tabFill
  if o.Background == ns.SOLID then
    tabFill = { Color = o.Color }
  elseif o.BackgroundTileSize ~= nil then
    tabFill = { Texture = o.Background, HorizTile = true, VertTile = true, VertexColor = o.Color }
  else
    tabFill = { Texture = o.Background, VertexColor = o.Color }
  end
  local elements = {
    SectionHeader = { Font = ns.WHITE },
    Tab = ns.Tab({
      Fill = tabFill,
      Edge = o.TabEdge,
      Accent = o.TabAccent,
      EdgeSize = o.TabEdgeSize,
      Font = o.TabFont or ns.WHITE_OUTLINE,
    }),
  }
  if o.Crest ~= nil then
    local scale = o.CrestScale or 0.25
    local art = { Texture = o.Crest, TexCoords = { 0, 1, 0, 1 }, Width = 275 * scale, Height = 350 * scale }
    elements.BagButton = {
      Portrait = art,
      -- Blizzard's highlight sits 2 to the right of the portrait, scaled with the crest.
      Highlight = { Texture = o.Crest, TexCoords = { 0, 1, 0, 1 }, Width = art.Width, Height = art.Height, X = 2 * scale },
    }
  end

  return {
    Name = o.Name,
    DisplayName = o.DisplayName,
    Description = o.Description,
    Parent = "Default",
    Windows = {
      Bag = {
        Template = false,
        Backdrop = backdrop(o.Color, o.BackgroundInset),
        Textures = bagTextures,
        Title = bagTitle,
        CloseButton = {
          Template = "UIPanelCloseButtonNoScripts",
          Points = { { Point = "TOPRIGHT", X = o.Close.X, Y = o.Close.Y } },
        },
        Layout = {
          -- In the band above the content, which it never pushes down.
          Search = { Points = o.Search, Reserve = 0 },
          MenuButton = { Points = { { Point = "TOPLEFT", X = o.Menu.X, Y = o.Menu.Y } } },
          -- Below the border (or the fill, where it reaches further).
          Tabs = ns.TabsBelow(math.max(o.ArtBelow or o.Outset, o.BackgroundInset), o.TabsX),
        },
      },
      Panel = {
        Template = false,
        Backdrop = backdrop(o.PanelColor or o.Color, o.BackgroundInset),
        Textures = { border },
        Title = { Font = titleFont, Points = { { Point = "TOP" } }, Height = 30 },
        CloseButton = {
          Template = "UIPanelCloseButtonNoScripts",
          Points = { { Point = "TOPRIGHT", X = 1, Y = 0 } },
        },
      },
      Dialog = flat,
      Slots = slots,
    },
    Elements = elements,
  }
end

-- Placeholder builds a theme that is not finished yet: hidden from the theme picker, drawn
-- like BetterBags' Simple Dark.
---@param name string
---@param displayName string
---@param description string
---@return table
function ns.Placeholder(name, displayName, description)
  return {
    Name = name,
    DisplayName = displayName,
    Description = description,
    Parent = "SimpleDark",
    Hidden = true,
  }
end

---@class MacOSThemeOptions
---@field Name string
---@field DisplayName string
---@field Description string
---@field Art string The prefix of the theme's art files (MacOSDark, MacOSLight).
---@field Color number[] The window's fill.
---@field Bottom number The bottom edge's height and slice margin.
---@field Sides boolean Draws the 2 pixel left and right edges.
---@field Tab table The tab's colors: ns.Tab options other than Font (Helvetica Neue).

-- MacOS builds a macOS window: a title bar above the window with the close and menu buttons
-- and the search box, an edge below it, and Helvetica Neue titles.
---@param o MacOSThemeOptions
---@return table
function ns.MacOS(o)
  local art = ns.TEXTURES .. o.Art
  local textures = {
    {
      Name = "TitleBar",
      Texture = art .. "BorderTop.png",
      SliceMargins = { Left = 8, Top = 20, Right = 8, Bottom = 0 },
      SliceMode = "Tiled",
      Points = { { Point = "TOPLEFT", Y = 32 }, { Point = "TOPRIGHT", Y = 32 } },
      Size = { Height = 32 },
      Opacity = true,
    },
    {
      Name = "Bottom",
      Texture = art .. "BorderBottom.png",
      SliceMargins = { Left = o.Bottom, Top = 0, Right = o.Bottom, Bottom = o.Bottom },
      SliceMode = "Tiled",
      Points = { { Point = "BOTTOMLEFT", Y = -o.Bottom }, { Point = "BOTTOMRIGHT", Y = -o.Bottom } },
      Size = { Height = o.Bottom },
      Opacity = true,
    },
  }
  if o.Sides then
    table.insert(textures, {
      Name = "Left",
      Texture = art .. "BorderLeft.png",
      VertTile = true,
      Points = { { Point = "TOPLEFT" }, { Point = "BOTTOMLEFT", X = 2 } },
      Size = { Width = 2 },
      Opacity = true,
    })
    table.insert(textures, {
      Name = "Right",
      Texture = art .. "BorderRight.png",
      VertTile = true,
      Points = { { Point = "TOPRIGHT" }, { Point = "BOTTOMRIGHT", X = -2 } },
      Size = { Width = 2 },
      Opacity = true,
    })
  end
  local font = ns.Font("HelveticaNeueRoman.otf", 12)
  local backdrop = {
    BgFile = "Interface\\ChatFrame\\ChatFrameBackground",
    Tile = true,
    TileSize = 128,
    Color = o.Color,
  }
  local close = {
    Size = 12,
    Points = { { Point = "TOPLEFT", X = 6, Y = 22 } },
    Normal = { Texture = art .. "CloseButton.png" },
    Highlight = { Texture = art .. "CloseButton.png", BlendMode = "ADD" },
    Pushed = { Texture = art .. "CloseButton.png" },
  }
  local flat = {
    Template = false,
    Backdrop = backdrop,
    Textures = textures,
    Title = { Font = font, Points = { { Point = "TOPLEFT", X = 4, Y = 20 } }, Height = 30 },
  }
  local slots = {}
  for k, v in pairs(flat) do
    slots[k] = v
  end
  slots.Layout = ABOVE_THE_BAG
  local menu = art .. "MenuButton.png"
  local tab = { Font = font }
  for k, v in pairs(o.Tab) do
    tab[k] = v
  end
  return {
    Name = o.Name,
    DisplayName = o.DisplayName,
    Description = o.Description,
    Parent = "Default",
    Windows = {
      Bag = {
        Template = false,
        Backdrop = backdrop,
        Textures = textures,
        Title = { Font = font, Points = { { Point = "TOP" } }, Height = 30 },
        CloseButton = close,
        Layout = {
          Search = { Points = ns.SearchPoints("TOP", 0, 26), Reserve = 0 },
          MenuButton = { Points = { { Point = "TOPLEFT", X = 24, Y = 22 } } },
          -- Below the bottom edge.
          Tabs = ns.TabsBelow(o.Bottom),
        },
      },
      Panel = {
        Template = false,
        Backdrop = backdrop,
        Textures = textures,
        Title = { Font = font, Points = { { Point = "TOP" } }, Height = 30 },
        CloseButton = close,
      },
      Dialog = flat,
      Slots = slots,
    },
    Elements = {
      SectionHeader = { Font = font },
      Tab = ns.Tab(tab),
      BagButton = {
        Size = 12,
        Portrait = false,
        Highlight = false,
        States = {
          Normal = { Texture = menu },
          Highlight = { Texture = menu, BlendMode = "ADD" },
          Pushed = { Texture = menu },
        },
      },
    },
  }
end
