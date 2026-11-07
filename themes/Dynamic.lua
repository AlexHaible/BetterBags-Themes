local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

-- Dynamic is the theme of the player's own race: it inherits everything from that race's theme (Sonata resolves a
-- theme's Parent when it applies it), keeping its own name. Listed after every race theme in the TOC, so they are
-- registered by now.

-- Race file names (UnitRace's second value) whose theme is not named after them.
local THEMES = {
  Scourge = "RacesUndead",
  EarthenDwarf = "RacesEarthen",
  -- Haranir's own name is "Haranir" (matched by default); earlier builds spelled it so.
  Harronir = "RacesHaranir",
}
-- Races told apart only by their ID (UnitRace's third value): Forever's Skyborne are both "Skyborne".
local BY_ID = {
  [95] = "RacesHighOrderSkyborne",
  [96] = "RacesWindshaperSkyborne",
}
-- A race with no theme of its own takes its faction's.
local BY_FACTION = {
  Alliance = "RacesHuman",
  Horde = "RacesOrc",
  Neutral = "RacesPandaren",
}

-- usable says whether a race theme is registered and finished (a placeholder is hidden).
---@param name string
---@return boolean
local function usable(name)
  local theme = sonata:GetTheme(name)
  return theme ~= nil and theme.Hidden ~= true
end

---@return string
local function parent()
  local _, race, id = UnitRace("player")
  if id ~= nil and BY_ID[id] ~= nil and usable(BY_ID[id]) then
    return BY_ID[id]
  end
  if race ~= nil then
    local name = THEMES[race] or ("Races" .. race)
    if usable(name) then
      return name
    end
  end
  return BY_FACTION[UnitFactionGroup("player") or ""] or "RacesHuman"
end

sonata:RegisterTheme({
  Name = "RacesDynamic",
  DisplayName = "Races - Dynamic",
  Description = "A theme that changes depending on your race.",
  Parent = parent(),
})
