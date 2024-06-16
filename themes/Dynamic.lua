---@class BetterBags: AceAddon
local BetterBags = LibStub('AceAddon-3.0'):GetAddon("BetterBags")
assert(BetterBags, "BetterBags - Themes requires BetterBags")

---@class Themes: AceModule
local themes = BetterBags:GetModule('Themes')

---@class SimpleDarkDecoration: Frame
---@field title FontString

---@type table<string, SimpleDarkDecoration>
local decoratorFrames = {}

local playerRaceFull, playerRace, raceId = UnitRace("player")
local dynamicBgFile
local dynamicEdgeFile

-- Horde Races
if playerRace == "BloodElf" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Orc" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Undead" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Tauren" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Troll" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Goblin" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Nightborne" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "MagharOrc" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "HighmountainTauren" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "ZandalariTroll" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Vulpera" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'

-- Alliance Races
elseif playerRace == "NightElf" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Human" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Draenei" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Dwarf" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Gnome" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Worgen" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "DarkIronDwarf" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "LightforgedDraenei" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "VoidElf" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "KulTiran" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Mechagnome" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
  
-- Both faction races
elseif playerRace == "Dracthyr" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
elseif playerRace == "Pandaren" then
  dynamicBgFile = 'Interface\\ChatFrame\\ChatFrameBackground'
  dynamicEdgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border'
end

---@type Theme
local simpleDark = {
  Name = 'Races - Dynamic',
  Description = 'A theme that changes depending on your race.',
  Available = false,
  Portrait = function(frame)
    local decoration = decoratorFrames[frame:GetName()]
    if not decoration then
      -- Backdrop
      decoration = CreateFrame("Frame", frame:GetName().."ThemeSimpleDark", frame, "BackdropTemplate") --[[@as SimpleDarkDecoration]]
      decoration:SetAllPoints()
      decoration:SetFrameLevel(frame:GetFrameLevel() - 1)
      decoration:SetBackdrop({
        bgFile = dynamicBgFile,
        edgeFile = dynamicEdgeFile,
        edgeSize = 16,
        insets = {left = 4, right = 4, top = 4, bottom = 4}
      })
      decoration:SetBackdropColor(0, 0, 0, 1)
      decoration:SetBackdropBorderColor(0.5, 0.5, 0.5, 1)

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

      local close = CreateFrame("Button", nil, decoration, "UIPanelCloseButtonNoScripts")
      close:SetPoint("TOPRIGHT", decoration, "TOPRIGHT", 1, 0)
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
        bgFile = dynamicBgFile,
        edgeFile = dynamicEdgeFile,
        edgeSize = 16,
        insets = {left = 4, right = 4, top = 4, bottom = 4}
      })
      decoration:SetBackdropColor(0, 0, 0, 1)
      decoration:SetBackdropBorderColor(0.5, 0.5, 0.5, 1)

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
        bgFile = dynamicBgFile,
        edgeFile = dynamicEdgeFile,
        edgeSize = 16,
        insets = {left = 4, right = 4, top = 4, bottom = 4}
      })
      decoration:SetBackdropColor(0, 0, 0, 1)
      decoration:SetBackdropBorderColor(0.5, 0.5, 0.5, 1)

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

themes:RegisterTheme('RacesDynamic', simpleDark)