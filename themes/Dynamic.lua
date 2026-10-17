local _, ns = ...

---@class Sonata: AceModule
local sonata = LibStub('AceAddon-3.0'):GetAddon('BetterBags'):GetModule('Sonata')

-- Not finished yet: hidden from the theme picker.
sonata:RegisterTheme(ns.Placeholder("RacesDynamic", "Races - Dynamic", "A theme that changes depending on your race."))
