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

local theBorder = 'Interface\\AddOns\\BetterBags-Themes\\textures\\HumanBorder.png'
local theBackground = 'Interface\\ChatFrame\\ChatFrameBackground'
local theCrest = 'Interface\\AddOns\\BetterBags-Themes\\textures\\HumanCrest.png'

---@type Theme
local simpleDark = {
  Name = 'Races - Human',
  Description = 'A Human inspired theme.',
  Available = true,
  Portrait = function(frame)
    local decoration = decoratorFrames[frame:GetName()]
    if not decoration then
      -- Backdrop
      decoration = CreateFrame("Frame", frame:GetName().."ThemeHuman", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8}
      })
      decoration:SetBackdropColor(0.01, 0.01, 0.2, 0.7)

      decoration.Texture = decoration:CreateTexture();
      decoration.Texture:SetTexture(theBorder)
      decoration.Texture:SetTextureSliceMargins(54, 54, 54, 54);
      decoration.Texture:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Texture:SetPoint("TOPLEFT", frame, "TOPLEFT", -16, 16)
      decoration.Texture:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 16, -16)
      decoration.Texture:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.UnitFrame12White)
      title:SetPoint("TOP", decoration, "TOP", 0, 24)
      title:SetHeight(30)
      decoration.title = title

      if themes.titles[frame:GetName()] then
        decoration.title:SetText(themes.titles[frame:GetName()])
      end

      local close = CreateFrame("Button", nil, decoration, "UIPanelCloseButtonNoScripts")
      close:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", 16, 16)
      close:SetScript("OnClick", function()
        frame.Owner:Hide()
      end)

      local searchBox = search:CreateBox(frame.Owner.kind, decoration --[[@as Frame]])
      searchBox.frame:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", -22, -2)
      searchBox.frame:SetSize(150, 20)
      decoration.search = searchBox

      local bagButton = themes.SetupBagButton(frame.Owner, decoration --[[@as Frame]])
      bagButton:SetPoint("TOPLEFT", decoration, "TOPLEFT", -24, 24)
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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeHuman", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8}
      })
      decoration:SetBackdropColor(0.01, 0.01, 0.2, 0.7)

      decoration.Texture = decoration:CreateTexture();
      decoration.Texture:SetTexture(theBorder)
      decoration.Texture:SetTextureSliceMargins(54, 54, 54, 54);
      decoration.Texture:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Texture:SetPoint("TOPLEFT", frame, "TOPLEFT", -16, 16)
      decoration.Texture:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 16, -16)
      decoration.Texture:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.UnitFrame12White)
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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeHuman", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8}
      })
      decoration:SetBackdropColor(0.01, 0.01, 0.2, 0.7)

      decoration.Texture = decoration:CreateTexture();
      decoration.Texture:SetTexture(theBorder)
      decoration.Texture:SetTextureSliceMargins(54, 54, 54, 54);
      decoration.Texture:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Texture:SetPoint("TOPLEFT", frame, "TOPLEFT", -16, 16)
      decoration.Texture:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 16, -16)
      decoration.Texture:SetVertexColor(1, 1, 1);

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
    return -40
  end
}

themes:RegisterTheme('RacesHuman', simpleDark)