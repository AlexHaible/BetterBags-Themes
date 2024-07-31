---@class BetterBags: AceAddon
local BetterBags = LibStub('AceAddon-3.0'):GetAddon("BetterBags")
assert(BetterBags, "BetterBags - Themes requires BetterBags")

---@class Themes: AceModule
local themes = BetterBags:GetModule('Themes')

---@class SearchBox: AceModule
local search = BetterBags:GetModule('SearchBox')

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
local theBorder = 'Interface\\AddOns\\BetterBags-Themes\\textures\\VulperaBorder.png'
local theBackground = 'Interface\\AddOns\\BetterBags-Themes\\textures\\SandDuneBackground.png'
local theCrest = 'Interface\\AddOns\\BetterBags-Themes\\textures\\VulperaCrest.png'

fonts.UnitFrame12WhiteTitle = CreateFont('BetterBagsUnitFrame12WhiteTitle')
fonts.UnitFrame12WhiteTitle:SetFont(UNIT_NAME_FONT, 12, "OUTLINE")
fonts.UnitFrame12WhiteTitle:SetTextColor(1, 1, 1)

---@type Theme
local simpleDark = {
  Name = 'Races - Vulpera',
  Description = 'A Vulpera inspired theme.',
  Available = true,
  Portrait = function(frame)
    local decoration = decoratorFrames[frame:GetName()]
    if not decoration then
      -- Backdrop
      decoration = CreateFrame("Frame", frame:GetName().."ThemeVulpera", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -12, right = -12, top = -12, bottom = -12},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(0.6470588235294118, 0.5568627450980392, 0.35294117647058826, 1)

      decoration.Border = decoration:CreateTexture();
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(30, 30, 30, 30);
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", -30, 30)
      decoration.Border:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 30, -30)
      decoration.Border:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.UnitFrame12WhiteTitle)
      title:SetPoint("TOP", decoration, "TOP", 0, 32)
      title:SetHeight(30)
      decoration.title = title

      if themes.titles[frame:GetName()] then
        decoration.title:SetText(themes.titles[frame:GetName()])
      end

      local close = CreateFrame("Button", nil, decoration, "UIPanelCloseButtonNoScripts")
      close:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", 28, 28)
      close:SetScript("OnClick", function()
        frame.Owner:Hide()
      end)

      local searchBox = search:CreateBox(frame.Owner.kind, decoration --[[@as Frame]])
      searchBox.frame:SetPoint("TOP", decoration, "TOP", 0, 0)
      searchBox.frame:SetSize(150, 20)
      decoration.search = searchBox

      local bagButton = themes.SetupBagButton(frame.Owner, decoration --[[@as Frame]])
      bagButton:SetPoint("TOPLEFT", decoration, "TOPLEFT", -32, 32)
      bagButton.portrait:SetSize(275, 350)
      bagButton.portrait:SetTexCoord(0, 1, 0, 1)
      bagButton.portrait:SetTexture(theCrest)
      bagButton.portrait:SetScale(0.25)
      bagButton.highlightTex:SetSize(275, 350)
      bagButton.highlightTex:SetTexCoord(0, 1, 0, 1)
      bagButton.highlightTex:SetTexture(theCrest)
      bagButton.highlightTex:SetScale(0.25)

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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeVulpera", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -12, right = -12, top = -12, bottom = -12},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(0.6470588235294118, 0.5568627450980392, 0.35294117647058826, 1)

      decoration.Border = decoration:CreateTexture();
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(30, 30, 30, 30);
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", -30, 30)
      decoration.Border:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 30, -30)
      decoration.Border:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.UnitFrame12WhiteTitle)
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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeVulpera", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -12, right = -12, top = -12, bottom = -12},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(0.6470588235294118, 0.5568627450980392, 0.35294117647058826, 1)

      decoration.Border = decoration:CreateTexture();
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(30, 30, 30, 30);
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", -30, 30)
      decoration.Border:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 30, -30)
      decoration.Border:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.UnitFrame12White)
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
    return -60
  end
}

themes:RegisterTheme('RacesVulpera', simpleDark)