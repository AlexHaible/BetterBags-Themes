---@class BetterBags: AceAddon
local BetterBags = LibStub('AceAddon-3.0'):GetAddon("BetterBags")
assert(BetterBags, "BetterBags - Themes requires BetterBags")

---@class Themes: AceModule
local themes = BetterBags:GetModule('Themes')

---@class Search: AceModule
local search = BetterBags:GetModule('Search')

---@class Fonts: AceModule
local fonts = BetterBags:GetModule('Fonts')

---@class SimpleDarkDecoration: Frame
---@field title FontString

---@type table<string, SimpleDarkDecoration>
local decoratorFrames = {}

---@type string
local theBorder = "Interface\\Addons\\BetterBags-Themes\\textures\\ArtDecoBorder.png"
local theBackground = "Interface\\Azerite\\AzeriteTooltipBackground"
local theFont = "Interface\\Addons\\BetterBags-Themes\\fonts\\PoiretOne-Regular.ttf"
--local theCrest = "Interface\\Addons\\BetterBags-Themes\\textures\\ArtDecoCrest.png"

fonts.ArtDeco = CreateFont('BetterBagsArtDeco')
fonts.ArtDeco:SetFont(theFont, 12, "")
fonts.ArtDeco:SetTextColor(1, 1, 1)

---@type Theme
local simpleDark = {
  Name = 'Art Deco',
  Description = 'An extravagant Art Deco theme.',
  Available = true,
  Portrait = function(frame)
    local decoration = decoratorFrames[frame:GetName()]
    if not decoration then
      -- Backdrop
      decoration = CreateFrame("Frame", frame:GetName().."ThemeArtDeco", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8}
      })
      decoration:SetBackdropColor(1, 1, 1, 1)

      decoration.Texture = decoration:CreateTexture();
      decoration.Texture:SetTexture(theBorder)
      decoration.Texture:SetTextureSliceMargins(64, 64, 64, 64);
      decoration.Texture:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Texture:SetPoint("TOPLEFT", frame, "TOPLEFT", -16, 16)
      decoration.Texture:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 16, -16)
      decoration.Texture:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.ArtDeco)
      title:SetPoint("TOP", decoration, "TOP", 0, 0)
      title:SetFont(theFont, 24, "")
      decoration.title = title

      if themes.titles[frame:GetName()] then
        decoration.title:SetText(themes.titles[frame:GetName()])
      end

      local close = CreateFrame("Button", nil, decoration, "UIPanelCloseButtonNoScripts")
      close:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", 16, 16)
      close:SetScript("OnClick", function()
        frame:Hide()
      end)

      local searchBox = search:CreateBox(frame.Owner.kind, decoration --[[@as Frame]])
      searchBox.frame:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", -22, -2)
      searchBox.frame:SetSize(150, 20)
      decoration.search = searchBox

      themes.SetupBagButton(frame.Owner, decoration --[[@as Frame]])
      -- Save the decoration frame for reuse.
      decoratorFrames[frame:GetName()] = decoration
    else
      decoration:Show()
    end
  end,
  Simple = function(frame)
    local decoration = decoratorFrames[frame:GetName()]
    if not decoration then
      -- Backdrop
      decoration = CreateFrame("Frame", frame:GetName().."ThemeArtDeco", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8}
      })
      decoration:SetBackdropColor(1, 1, 1, 1)

      decoration.Texture = decoration:CreateTexture();
      decoration.Texture:SetTexture(theBorder)
      decoration.Texture:SetTextureSliceMargins(64, 64, 64, 64);
      decoration.Texture:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Texture:SetPoint("TOPLEFT", frame, "TOPLEFT", -16, 16)
      decoration.Texture:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 16, -16)
      decoration.Texture:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.ArtDeco)
      title:SetPoint("TOP", decoration, "TOP", 0, 0)
      title:SetHeight(30)
      decoration.title = title

      local close = CreateFrame("Button", nil, decoration, "UIPanelCloseButtonNoScripts")
      close:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", 1, 0)
      close:SetScript("OnClick", function()
        frame:Hide()
      end)

      if themes.titles[frame:GetName()] then
        decoration.title:SetText(themes.titles[frame:GetName()])
      end
      -- Save the decoration frame for reuse.
      decoratorFrames[frame:GetName()] = decoration
    else
      decoration:Show()
    end
  end,
  Flat = function (frame)
    local decoration = decoratorFrames[frame:GetName()]
    if not decoration then
      -- Backdrop
      decoration = CreateFrame("Frame", frame:GetName().."ThemeArtDeco", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8}
      })
      decoration:SetBackdropColor(1, 1, 1, 1)

      decoration.Texture = decoration:CreateTexture();
      decoration.Texture:SetTexture(theBorder)
      decoration.Texture:SetTextureSliceMargins(64, 64, 64, 64);
      decoration.Texture:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Texture:SetPoint("TOPLEFT", frame, "TOPLEFT", -16, 16)
      decoration.Texture:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 16, -16)
      decoration.Texture:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.ArtDeco)
      title:SetPoint("TOP", decoration, "TOP", 0, 0)
      title:SetHeight(30)
      decoration.title = title

      if themes.titles[frame:GetName()] then
        decoration.title:SetText(themes.titles[frame:GetName()])
      end
      -- Save the decoration frame for reuse.
      decoratorFrames[frame:GetName()] = decoration
    else
      decoration:Show()
    end
  end,
  Opacity = function(frame, alpha)
    local decoration = decoratorFrames[frame:GetName()]
    if decoration then
      decoration:SetAlpha(alpha / 100)
    end
  end,
  SectionFont = function(font)
    font:SetFontObject(fonts.UnitFrame12White)
  end,
  SetTitle = function(frame, title)
    local decoration = decoratorFrames[frame:GetName()]
    if decoration then
      decoration.title:SetText(title)
    end
  end,
  Reset = function()
    for _, frame in pairs(decoratorFrames) do
      frame:Hide()
    end
  end,
  ToggleSearch = function (frame, shown)
    local decoration = decoratorFrames[frame:GetName()]
    if decoration then
      decoration.search:SetShown(shown)
    end
  end,
  PositionBagSlots = function (frame, bagSlotWindow)
    bagSlotWindow:ClearAllPoints()
    bagSlotWindow:SetPoint("BOTTOMLEFT", frame, "TOPLEFT", 0, 0)
  end,
  OffsetSidebar = function()
    return -40
  end
}

themes:RegisterTheme('ThemesArtDeco', simpleDark)