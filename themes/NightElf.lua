---@class BetterBags: AceAddon
local BetterBags = LibStub('AceAddon-3.0'):GetAddon("BetterBags")
assert(BetterBags, "BetterBags - Themes requires BetterBags")

---@class Themes: AceModule
local themes = BetterBags:GetModule('Themes')

---@class Search: AceModule
local search = BetterBags:GetModule('Search')

---@class SimpleDarkDecoration: Frame
---@field title FontString

---@class BagButton: Button
---@field portrait Texture
---@field highlightTex Texture

---@type table<string, SimpleDarkDecoration>
local decoratorFrames = {}

local theBorder = 'Interface\\AddOns\\BetterBags-Themes\\textures\\NightElfBorder.png'
local theBackground = 'Interface\\ChatFrame\\ChatFrameBackground'

---@type Theme
local simpleDark = {
  Name = 'Races - Night Elf',
  Description = 'A Night Elf inspired theme.',
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
        insets = {left = -8, right = -8, top = -8, bottom = -8}
      })
      decoration:SetBackdropColor(0.01, 0.2, 0.01, 0.7)

      decoration.Texture = decoration:CreateTexture();
      decoration.Texture:SetTexture(theBorder)
      decoration.Texture:SetTextureSliceMargins(74, 74, 74, 74);
      decoration.Texture:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Texture:SetPoint("TOPLEFT", frame, "TOPLEFT", -24, 24)
      decoration.Texture:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 24, -24)
      decoration.Texture:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      title:SetFont(UNIT_NAME_FONT, 14, "OUTLINE")
      title:SetTextColor(1, 1, 1)
      title:SetPoint("TOP", decoration, "TOP", 0, 20)
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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeSimpleDark", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8}
      })
      decoration:SetBackdropColor(0.01, 0.2, 0.01, 0.7)

      decoration.Texture = decoration:CreateTexture();
      decoration.Texture:SetTexture(theBorder)
      decoration.Texture:SetTextureSliceMargins(74, 74, 74, 74);
      decoration.Texture:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Texture:SetPoint("TOPLEFT", frame, "TOPLEFT", -24, 24)
      decoration.Texture:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 24, -24)
      decoration.Texture:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      title:SetFont(UNIT_NAME_FONT, 12, "")
      title:SetTextColor(1, 1, 1)
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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeSimpleDark", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8}
      })
      decoration:SetBackdropColor(0.01, 0.2, 0.01, 0.7)

      decoration.Texture = decoration:CreateTexture();
      decoration.Texture:SetTexture(theBorder)
      decoration.Texture:SetTextureSliceMargins(74, 74, 74, 74);
      decoration.Texture:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Texture:SetPoint("TOPLEFT", frame, "TOPLEFT", -24, 24)
      decoration.Texture:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 24, -24)
      decoration.Texture:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      title:SetFont(UNIT_NAME_FONT, 12, "")
      title:SetTextColor(1, 1, 1)
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
    font:SetFont(UNIT_NAME_FONT, 12, "")
    font:SetTextColor(1, 1, 1)
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
  end
}

themes:RegisterTheme('RacesNightElf', simpleDark)