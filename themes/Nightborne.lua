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
local theBorder = 'Interface\\AddOns\\BetterBags-Themes\\textures\\NightborneBorder.png'
local theBackground = 'Interface\\AddOns\\BetterBags-Themes\\textures\\SuramarGrassBackground.png'
local theCrest = 'Interface\\AddOns\\BetterBags-Themes\\textures\\NightborneCrest.png'
local theFlower = 'Interface\\AddOns\\BetterBags-Themes\\textures\\NightborneFlower.png'
local theRuneCircle = 'Interface\\AddOns\\BetterBags-Themes\\textures\\NightborneRuneCircle.png'

fonts.UnitFrame12WhiteTitle = CreateFont('BetterBagsUnitFrame12WhiteTitle')
fonts.UnitFrame12WhiteTitle:SetFont(UNIT_NAME_FONT, 12, "OUTLINE")
fonts.UnitFrame12WhiteTitle:SetTextColor(1, 1, 1)

---@type Theme
local simpleDark = {
  Name = 'Races - Nightborne',
  Description = 'A Nightborne inspired theme.',
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
        insets = {left = -32, right = -32, top = -32, bottom = -32},
        tile = true,
        tileSize = 256
      })
      decoration:SetBackdropColor(1, 1, 1, 1)

      decoration.Border = decoration:CreateTexture()
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(32, 32, 32, 32);
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", -32, 32)
      decoration.Border:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 32, -32)
      decoration.Border:SetVertexColor(1, 1, 1)

      decoration.Flower1 = decoration:CreateTexture()
      decoration.Flower1:SetTexture(theFlower)
      decoration.Flower1:SetSize(64, 64)
      decoration.Flower1:SetPoint("TOPLEFT", frame, "TOPLEFT", -48, 48)
      decoration.Flower1:SetVertexColor(1, 1, 1)
      decoration.Flower1:SetDrawLayer("OVERLAY", 1)

      decoration.Flower2 = decoration:CreateTexture()
      decoration.Flower2:SetTexture(theFlower)
      decoration.Flower2:SetSize(64, 64)
      decoration.Flower2:SetPoint("TOPRIGHT", frame, "TOPRIGHT", 48, 48)
      decoration.Flower2:SetVertexColor(1, 1, 1)
      decoration.Flower1:SetDrawLayer("OVERLAY", 1)

      decoration.Flower3 = decoration:CreateTexture()
      decoration.Flower3:SetTexture(theFlower)
      decoration.Flower3:SetSize(64, 64)
      decoration.Flower3:SetPoint("BOTTOMLEFT", frame, "BOTTOMLEFT", -48, -48)
      decoration.Flower3:SetVertexColor(1, 1, 1)
      decoration.Flower1:SetDrawLayer("OVERLAY", 1)

      decoration.Flower4 = decoration:CreateTexture()
      decoration.Flower4:SetTexture(theFlower)
      decoration.Flower4:SetSize(64, 64)
      decoration.Flower4:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 48, -48)
      decoration.Flower4:SetVertexColor(1, 1, 1)
      decoration.Flower1:SetDrawLayer("OVERLAY", 1)

      decoration.RuneCircle1 = decoration:CreateTexture()
      decoration.RuneCircle1:SetTexture(theRuneCircle)
      decoration.RuneCircle1:SetSize(64, 64)
      decoration.RuneCircle1:SetPoint("TOPLEFT", frame, "TOPLEFT", -48, 48)
      decoration.RuneCircle1:SetVertexColor(1, 1, 1)
      decoration.Flower1:SetDrawLayer("OVERLAY", 2)

      decoration.RuneCircle2 = decoration:CreateTexture()
      decoration.RuneCircle2:SetTexture(theRuneCircle)
      decoration.RuneCircle2:SetSize(64, 64)
      decoration.RuneCircle2:SetPoint("TOPRIGHT", frame, "TOPRIGHT", 48, 48)
      decoration.RuneCircle2:SetVertexColor(1, 1, 1)
      decoration.Flower1:SetDrawLayer("OVERLAY", 2)

      decoration.RuneCircle3 = decoration:CreateTexture()
      decoration.RuneCircle3:SetTexture(theRuneCircle)
      decoration.RuneCircle3:SetSize(64, 64)
      decoration.RuneCircle3:SetPoint("BOTTOMLEFT", frame, "BOTTOMLEFT", -48, -48)
      decoration.RuneCircle3:SetVertexColor(1, 1, 1)
      decoration.Flower1:SetDrawLayer("OVERLAY", 2)

      decoration.RuneCircle4 = decoration:CreateTexture()
      decoration.RuneCircle4:SetTexture(theRuneCircle)
      decoration.RuneCircle4:SetSize(64, 64)
      decoration.RuneCircle4:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 48, -48)
      decoration.RuneCircle4:SetVertexColor(1, 1, 1)
      decoration.Flower1:SetDrawLayer("OVERLAY", 2)

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.UnitFrame12WhiteTitle)
      title:SetPoint("TOP", decoration, "TOP", 0, 30)
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
      searchBox.frame:SetPoint("TOP", decoration, "TOP", 0, -8)
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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeSimpleDark", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -32, right = -32, top = -32, bottom = -32},
        tile = true,
        tileSize = 256
      })
      decoration:SetBackdropColor(1, 1, 1, 1)

      decoration.Border = decoration:CreateTexture()
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(32, 32, 32, 32);
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", -32, 32)
      decoration.Border:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 32, -32)
      decoration.Border:SetVertexColor(1, 1, 1)

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
      decoration = CreateFrame("Frame", frame:GetName().."ThemeSimpleDark", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = theBackground,
        insets = {left = -32, right = -32, top = -32, bottom = -32},
        tile = true,
        tileSize = 256
      })
      decoration:SetBackdropColor(1, 1, 1, 1)

      decoration.Border = decoration:CreateTexture()
      decoration.Border:SetTexture(theBorder)
      decoration.Border:SetTextureSliceMargins(32, 32, 32, 32);
      decoration.Border:SetTextureSliceMode(Enum.UITextureSliceMode.Tiled);
      decoration.Border:SetPoint("TOPLEFT", frame, "TOPLEFT", -32, 32)
      decoration.Border:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", 32, -32)
      decoration.Border:SetVertexColor(1, 1, 1)

      -- Title text
      local title = decoration:CreateFontString(nil, "OVERLAY")
      title:SetFontObject(fonts.UnitFrame12WhiteTitle)
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

themes:RegisterTheme('RacesNightborne', simpleDark)