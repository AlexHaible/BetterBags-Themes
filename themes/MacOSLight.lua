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

---@class BagButton: Button
---@field portrait Texture
---@field highlightTex Texture

---@type table<string, SimpleDarkDecoration>
local decoratorFrames = {}

---@type string
local theBorder = 'Interface\\AddOns\\BetterBags-Themes\\textures\\MacOSLightBorderTop.png'
local theBottomBorder = 'Interface\\AddOns\\BetterBags-Themes\\textures\\MacOSLightBorderBottom.png'
local theBackground = 'Interface\\ChatFrame\\ChatFrameBackground'
local theSearchBox = 'Interface\\AddOns\\BetterBags-Themes\\textures\\MacOSLightSearch.png'
local closeButton = 'Interface\\AddOns\\BetterBags-Themes\\textures\\MacOSLightCloseButton.png'
local menuButton = 'Interface\\AddOns\\BetterBags-Themes\\textures\\MacOSLightMenuButton.png'
local theFont = 'Interface\\AddOns\\BetterBags-Themes\\fonts\\HelveticaNeueRoman.otf'

fonts.HelveticaNeue = CreateFont('BetterBagsHelveticaNeue')
fonts.HelveticaNeue:SetFont(theFont, 12, "")
fonts.HelveticaNeue:SetTextColor(1, 1, 1)

---@type Theme
local simpleDark = {
  Name = 'MacOS - Light',
  Description = 'A MacOS inspired theme.',
  Available = true,
  Portrait = function(frame)
    local decoration = decoratorFrames[frame:GetName()]
    if not decoration then
      -- Backdrop
      decoration = CreateFrame("Frame", frame:GetName().."ThemeMacOSLight", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -0, right = -0, top = -0, bottom = -0},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(1, 1, 1, 0.5)

      decoration.Border = decoration:CreateTexture()
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(8, 20, 8, 0)
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled)
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", 0, 32)
      decoration.Border:SetPoint("TOPRIGHT", frame, "TOPRIGHT", 0, 32)
      decoration.Border:SetVertexColor(1, 1, 1)

      decoration.BottomBorder = decoration:CreateTexture()
      decoration.BottomBorder:SetTexture(theBottomBorder)
      decoration.BottomBorder:SetTextureSliceMargins(5, 0, 5, 5)
      decoration.BottomBorder:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled)
      decoration.BottomBorder:SetPoint("BOTTOMLEFT", frame, "BOTTOMLEFT", 0, -5)
      decoration.BottomBorder:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 0, -5)
      decoration.BottomBorder:SetVertexColor(1, 1, 1)

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.HelveticaNeue)
      title:SetPoint("TOP", decoration, "TOP", 0, 0)
      title:SetHeight(30)
      decoration.title = title

      if themes.titles[frame:GetName()] then
        decoration.title:SetText(themes.titles[frame:GetName()])
      end

      local close = CreateFrame("Button", nil, decoration)
      close:SetSize(12, 12)
      close:SetNormalTexture(closeButton)
      close:SetHighlightTexture(closeButton, "ADD")
      close:SetPushedTexture(closeButton)
      close:SetPoint("TOPLEFT", decoration, "TOPLEFT", 6, 22)
      close:SetScript("OnClick", function()
        frame:Hide()
      end)

      local searchBox = search:CreateBox(frame.Owner.kind, decoration --[[@as Frame]])
      searchBox.frame:SetPoint("TOP", decoration, "TOP", 0, 26)
      searchBox.frame:SetSize(150, 20)
      searchBox.frame:SetFrameLevel(decoration:GetFrameLevel() + 1)
      decoration.search = searchBox

      local bagButton = themes.SetupBagButton(frame.Owner, decoration --[[@as Frame]])
      bagButton.portrait:Hide()
      bagButton.highlightTex:Hide()
      bagButton:ClearAllPoints()
      bagButton:SetSize(12, 12)
      bagButton:SetNormalTexture(menuButton)
      bagButton:SetHighlightTexture(menuButton, "ADD")
      bagButton:SetPushedTexture(menuButton)
      bagButton:SetPoint("TOPLEFT", decoration, "TOPLEFT", 24, 22)

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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeMacOSLight", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -0, right = -0, top = -0, bottom = -0},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(1, 1, 1, 0.5)

      decoration.Border = decoration:CreateTexture()
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(8, 20, 8, 0)
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled)
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", 0, 32)
      decoration.Border:SetPoint("TOPRIGHT", frame, "TOPRIGHT", 0, 32)
      decoration.Border:SetVertexColor(1, 1, 1)

      decoration.BottomBorder = decoration:CreateTexture()
      decoration.BottomBorder:SetTexture(theBottomBorder)
      decoration.BottomBorder:SetTextureSliceMargins(5, 0, 5, 5)
      decoration.BottomBorder:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled)
      decoration.BottomBorder:SetPoint("BOTTOMLEFT", frame, "BOTTOMLEFT", 0, -5)
      decoration.BottomBorder:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 0, -5)
      decoration.BottomBorder:SetVertexColor(1, 1, 1)

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.HelveticaNeue)
      title:SetPoint("TOP", decoration, "TOP", 0, 0)
      title:SetHeight(30)
      decoration.title = title

      local close = CreateFrame("Button", nil, decoration)
      close:SetSize(12, 12)
      close:SetNormalTexture(closeButton)
      close:SetHighlightTexture(closeButton, "ADD")
      close:SetPushedTexture(closeButton)
      close:SetPoint("TOPLEFT", decoration, "TOPLEFT", 6, 22)
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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeMacOSLight", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -0, right = -0, top = -0, bottom = -0},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(1, 1, 1, 0.5)

      decoration.Border = decoration:CreateTexture()
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(8, 20, 8, 0)
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled)
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", 0, 32)
      decoration.Border:SetPoint("TOPRIGHT", frame, "TOPRIGHT", 0, 32)
      decoration.Border:SetVertexColor(1, 1, 1)

      decoration.BottomBorder = decoration:CreateTexture()
      decoration.BottomBorder:SetTexture(theBottomBorder)
      decoration.BottomBorder:SetTextureSliceMargins(5, 0, 5, 5)
      decoration.BottomBorder:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled)
      decoration.BottomBorder:SetPoint("BOTTOMLEFT", frame, "BOTTOMLEFT", 0, -5)
      decoration.BottomBorder:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 0, -5)
      decoration.BottomBorder:SetVertexColor(1, 1, 1)

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      title:SetFontObject(fonts.HelveticaNeue)
      title:SetPoint("TOPLEFT", decoration, "TOPLEFT", 4, 20)
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
    font:SetFontObject(fonts.HelveticaNeue)
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
    return -20
  end
}

themes:RegisterTheme('MacOSLight', simpleDark)