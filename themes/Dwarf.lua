---@class BetterBags: AceAddon
local BetterBags = LibStub('AceAddon-3.0'):GetAddon("BetterBags")
assert(BetterBags, "BetterBags - Themes requires BetterBags")

---@class Themes: AceModule
local themes = BetterBags:GetModule('Themes')

---@class SimpleDarkDecoration: Frame
---@field title FontString

---@type table<string, SimpleDarkDecoration>
local decoratorFrames = {}

---@type string
local dwarfBorder = 'Interface\\AddOns\\BetterBags-Themes\\textures\\DwarfBorder.png'
local dwarfBackground = 'Interface\\AddOns\\BetterBags-Themes\\textures\\MarbleBackground.png'

---@type Theme
local simpleDark = {
  Name = 'Races - Dwarf',
  Description = 'A Dwarf inspired theme.',
  Available = true,
  Portrait = function(frame)
    local decoration = decoratorFrames[frame:GetName()]
    if not decoration then
      -- Backdrop
      decoration = CreateFrame("Frame", frame:GetName().."ThemeSimpleDark", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = dwarfBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(0.85, 0.85, 1, 1)

      decoration.Border = decoration:CreateTexture();
      decoration.Border:SetTexture(dwarfBorder)
      decoration.Border:SetTextureSliceMargins(52, 52, 52, 52);
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", -48, 48)
      decoration.Border:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 48, -48)
      decoration.Border:SetVertexColor(1, 1, 1);

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      title:SetFont(UNIT_NAME_FONT, 14, "OUTLINE")
      title:SetTextColor(1, 1, 1)
      title:SetPoint("TOP", decoration, "TOP", 0, 40)
      title:SetHeight(30)
      decoration.title = title

      if themes.titles[frame:GetName()] then
        decoration.title:SetText(themes.titles[frame:GetName()])
      end

      local close = CreateFrame("Button", nil, decoration, "UIPanelCloseButtonNoScripts")
      close:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", 36, 36)
      close:SetScript("OnClick", function()
        frame.Owner:Hide()
      end)

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
        bgFile = dwarfBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(0.85, 0.85, 1, 1)

      decoration.Border = decoration:CreateTexture();
      decoration.Border:SetTexture(dwarfBorder)
      decoration.Border:SetTextureSliceMargins(52, 52, 52, 52);
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", -48, 48)
      decoration.Border:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 48, -48)
      decoration.Border:SetVertexColor(1, 1, 1);

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
        bgFile = dwarfBackground,
        insets = {left = -8, right = -8, top = -8, bottom = -8},
        tile = true,
        tileSize = 128
      })
      decoration:SetBackdropColor(0.85, 0.85, 1, 1)

      decoration.Border = decoration:CreateTexture();
      decoration.Border:SetTexture(dwarfBorder)
      decoration.Border:SetTextureSliceMargins(52, 52, 52, 52);
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", -48, 48)
      decoration.Border:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 48, -48)
      decoration.Border:SetVertexColor(1, 1, 1);

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
  end
}

themes:RegisterTheme('RacesDwarf', simpleDark)