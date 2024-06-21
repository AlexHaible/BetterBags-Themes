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
local theBorder = 'Interface\\AddOns\\BetterBags-Themes\\textures\\AeroGlassBorder.png'
local theBackground = 'Interface\\ChatFrame\\ChatFrameBackground'
local theTexture = 'Interface\\AddOns\\BetterBags-Themes\\textures\\AeroGlassTexture.png'
local theFont = 'Interface\\AddOns\\BetterBags-Themes\\fonts\\SegoeUI.ttf'
local closeButton = 'Interface\\AddOns\\BetterBags-Themes\\textures\\AeroGlassCloseButton.png'
local closeButtonHover = 'Interface\\AddOns\\BetterBags-Themes\\textures\\AeroGlassCloseButtonHover.png'
local closeButtonPush = 'Interface\\AddOns\\BetterBags-Themes\\textures\\AeroGlassCloseButtonPush.png'

fonts.SegoeUI = CreateFont('BetterBagsSegoeUI')
fonts.SegoeUI:SetFont(theFont, 12, "")
fonts.SegoeUI:SetTextColor(1, 1, 1)

---@type Theme
local simpleDark = {
  Name = 'Aero Glass',
  Description = 'A Windows 7 inspired theme.',
  Available = true,
  Portrait = function(frame)
    local decoration = decoratorFrames[frame:GetName()]
    if not decoration then
      -- Backdrop
      decoration = CreateFrame("Frame", frame:GetName().."ThemeSimpleDark", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -0, right = -0, top = -0, bottom = -0},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(0.5568627450980392, 0.6980392156862745, 0.8588235294117647, 0.5)

      decoration.BackdropOverlay = decoration:CreateTexture()
      decoration.BackdropOverlay:SetTexture(theTexture)
      decoration.BackdropOverlay:SetPoint("TOP", frame, "TOP", -8, -8)
      decoration.BackdropOverlay:SetPoint("RIGHT", frame, "RIGHT", 8, -8)
      decoration.BackdropOverlay:SetPoint("BOTTOM", frame, "BOTTOM", 8, -8)
      decoration.BackdropOverlay:SetPoint("LEFT", frame, "LEFT", -8, 8)
      decoration.BackdropOverlay:SetVertexColor(1, 1, 1, 0.2)

      decoration.Border = decoration:CreateTexture();
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(8, 29, 8, 8)
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled)
      decoration.Border:SetPoint("TOP", frame, "TOP", 0, 20)
      decoration.Border:SetPoint("RIGHT", frame, "RIGHT", 8, 0)
      decoration.Border:SetPoint("BOTTOM", frame, "BOTTOM", 0, -8)
      decoration.Border:SetPoint("LEFT", frame, "LEFT", -8, 0)
      decoration.Border:SetVertexColor(1, 1, 1)

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      title:SetFont(theFont, 12, "")
      title:SetTextColor(1, 1, 1)
      title:SetPoint("TOPLEFT", decoration, "TOPLEFT", 32, 20)
      title:SetHeight(30)
      decoration.title = title

      if themes.titles[frame:GetName()] then
        decoration.title:SetText(themes.titles[frame:GetName()])
      end

      local close = CreateFrame("Button", nil, decoration)
      close:SetSize(50, 21)
      close:SetPushedTexture(closeButtonPush)
      close:SetHighlightTexture(closeButtonHover)
      close:SetNormalTexture(closeButton)
      close:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", 0, 20)
      close:SetScript("OnClick", function()
        frame:Hide()
      end)

      local searchBox = search:CreateBox(frame.Owner.kind, decoration --[[@as Frame]])
      searchBox.frame:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", -22, -2)
      searchBox.frame:SetSize(150, 20)
      decoration.search = searchBox

      local bagButton = themes.SetupBagButton(frame.Owner, decoration --[[@as Frame]])
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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeSimpleDark", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -0, right = -0, top = -0, bottom = -0},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(0.5568627450980392, 0.6980392156862745, 0.8588235294117647, 0.5)

      decoration.BackdropOverlay = decoration:CreateTexture()
      decoration.BackdropOverlay:SetTexture(theTexture)
      decoration.BackdropOverlay:SetPoint("TOP", frame, "TOP", -8, -8)
      decoration.BackdropOverlay:SetPoint("RIGHT", frame, "RIGHT", 8, -8)
      decoration.BackdropOverlay:SetPoint("BOTTOM", frame, "BOTTOM", 8, -8)
      decoration.BackdropOverlay:SetPoint("LEFT", frame, "LEFT", -8, 8)
      decoration.BackdropOverlay:SetVertexColor(1, 1, 1, 0.2)

      decoration.Border = decoration:CreateTexture();
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(8, 29, 8, 8)
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled)
      decoration.Border:SetPoint("TOP", frame, "TOP", 0, 20)
      decoration.Border:SetPoint("RIGHT", frame, "RIGHT", 8, 0)
      decoration.Border:SetPoint("BOTTOM", frame, "BOTTOM", 0, -8)
      decoration.Border:SetPoint("LEFT", frame, "LEFT", -8, 0)
      decoration.Border:SetVertexColor(1, 1, 1)

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      title:SetFont(theFont, 12, "")
      title:SetTextColor(1, 1, 1)
      title:SetPoint("TOPLEFT", decoration, "TOPLEFT", 4, 20)
      title:SetHeight(30)
      decoration.title = title

      local close = CreateFrame("Button", nil, decoration)
      close:SetSize(50, 21)
      close:SetPushedTexture(closeButtonPush)
      close:SetHighlightTexture(closeButtonHover)
      close:SetNormalTexture(closeButton)
      close:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", 0, 20)
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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeSimpleDark", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -0, right = -0, top = -0, bottom = -0},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(0.5568627450980392, 0.6980392156862745, 0.8588235294117647, 0.5)

      decoration.BackdropOverlay = decoration:CreateTexture()
      decoration.BackdropOverlay:SetTexture(theTexture)
      decoration.BackdropOverlay:SetPoint("TOP", frame, "TOP", -8, -8)
      decoration.BackdropOverlay:SetPoint("RIGHT", frame, "RIGHT", 8, -8)
      decoration.BackdropOverlay:SetPoint("BOTTOM", frame, "BOTTOM", 8, -8)
      decoration.BackdropOverlay:SetPoint("LEFT", frame, "LEFT", -8, 8)
      decoration.BackdropOverlay:SetVertexColor(1, 1, 1, 0.2)

      decoration.Border = decoration:CreateTexture();
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(8, 29, 8, 8)
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled)
      decoration.Border:SetPoint("TOP", frame, "TOP", 0, 20)
      decoration.Border:SetPoint("RIGHT", frame, "RIGHT", 8, 0)
      decoration.Border:SetPoint("BOTTOM", frame, "BOTTOM", 0, -8)
      decoration.Border:SetPoint("LEFT", frame, "LEFT", -8, 0)
      decoration.Border:SetVertexColor(1, 1, 1)

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      title:SetFont(theFont, 12, "")
      title:SetTextColor(1, 1, 1)
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
    font:SetFontObject(fonts.SegoeUI)
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

themes:RegisterTheme('WinAeroGlass', simpleDark)