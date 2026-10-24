local _, ns = ...

-- Races - Night Elf, for BetterBags Next: Darnassus at dusk. Great gnarled roots are the bag's inner border, top to
-- bottom on a full bag: one hugging the edge and dipping into the bag, one wandering out over the feather and back,
-- a tendril looping far out, gaps between them; fused where they meet and painted in dusky violet with lavender
-- moonlight on their rims, carved spirals, moss, two-toned leaves (teal-jade turning violet), magenta blossoms and
-- Teldrassil's glowing mushrooms. Where they reach into the bag they sink into its backdrop, and back roots drawn under
-- the bag reach out from beneath it, interlacing. A leafy bough grows from behind them and fronds sway on them; wisps
-- drift among them. On a small bag the roots are two thirds of the size, gripping its top and bottom corners and
-- hanging past them. The art is tools/next_ornaments.py's; the ornaments are drawn for a bag whose inner side is on
-- the left (the backpack) and BetterBags mirrors them for the bank.
local ART = ns.NEXT_TEXTURES .. "NightElf\\"

ns.RegisterNextTheme({
  Name = "RacesNightElf",
  DisplayName = "Races - Night Elf",
  Description = "Darnassus at dusk: great violet roots woven through the bag, two-toned leaves, blossoms, wisps.",

  Textures = {
    NightElfRoots = ART .. "roots.png",
    NightElfUnder = ART .. "under.png",
    NightElfBough = ART .. "bough.png",
    NightElfFrond = ART .. "frond.png",
    NightElfCornerTop = ART .. "corner_top.png",
    NightElfCornerBottom = ART .. "corner_bottom.png",
  },

  Palette = {
    -- Twilight violet.
    Body = { 0.05, 0.035, 0.09, 0.94 },
    -- Violet light washing the top of the bag.
    Wash = { 0.60, 0.45, 1.0, 0.12 },
    -- The accent: the leaves' teal-jade.
    Gold = { 0.55, 0.90, 0.78, 1 },
    -- Edges and lines: lavender moonlight.
    Lavender = { 0.80, 0.72, 1.0, 1 },
    Text = { 0.95, 0.93, 1.0, 1 },
    Muted = { 0.66, 0.60, 0.80, 1 },
    Tab = { 0.08, 0.05, 0.13, 0.92 },
    TabSelected = { 0.18, 0.12, 0.28, 0.96 },
    Card = { 0.10, 0.06, 0.16, 0.98 },
    SearchFill = { 0.13, 0.09, 0.21, 1 },
    SearchFillFocus = { 0.17, 0.12, 0.28, 1 },
    ButtonIcon = { 0.86, 0.82, 1.0, 1 },
    Bead = { 0.85, 0.95, 1.0, 1 },
    -- Wisps: soft cyan-blue lights.
    Wisp = { 0.45, 0.78, 1.0, 1 },
    WispLight = { 0.80, 0.92, 1.0, 1 },
    -- The settings window's controls, in violet.
    ControlFill = { 0.11, 0.08, 0.18, 1 },
    ControlHover = { 0.15, 0.11, 0.25, 1 },
    ControlPressed = { 0.08, 0.06, 0.14, 1 },
    Track = { 0.22, 0.16, 0.32, 1 },
    Danger = { 1.0, 0.45, 0.55, 1 },
  },

  Panel = {
    Ornaments = {
      -- The back roots, under the bag's body and its feathered edge (the background layer, below them), so they reach
      -- out from beneath the bag, darkening as they near it: from the top of the screen to the bottom on a full bag.
      { Texture = "NightElfUnder", Point = "INNER", Width = 128, Tile = 512, X = -96, Layer = "BACKGROUND",
        SubLevel = -2, Sizes = "Full" },
      -- The bough grows from behind the front roots (a lower sublevel), its base at the middle of its art's right side,
      -- swaying slowly there.
      { Texture = "NightElfBough", Point = "TOPINNER", Anchor = "TOPOUTER", X = -14, Y = 220, Width = 128, Height = 128,
        Sizes = "Full", Motion = { Sway = 1.5, Period = 7, Delay = 0.8, Origin = "OUTER" } },
      -- The front roots, the bag's inner border from the top of the screen to the bottom: 128 wide, 96 of them out from
      -- the body and 32 in, where they sink into its backdrop; 4 pixels of art to a unit.
      { Texture = "NightElfRoots", Point = "INNER", Width = 128, Tile = 512, X = -96, Sizes = "Full", SubLevel = 1 },
      -- Fronds hung on the roots by their twig's base (near the art's bottom right), swaying, each its own way.
      { Texture = "NightElfFrond", Point = "TOPINNER", Anchor = "BOTTOMOUTER", X = -30, Y = 120, Width = 56,
        Height = 56, SubLevel = 2, Sizes = "Full", Motion = { Sway = 5, Period = 4.6, Origin = "BOTTOMOUTER" } },
      { Texture = "NightElfFrond", Point = "BOTTOMINNER", Anchor = "BOTTOMOUTER", X = -40, Y = -140, Width = 50,
        Height = 50, SubLevel = 2, Sizes = "Full", Motion = { Sway = 6, Period = 5.6, Delay = 2.1, Origin = "BOTTOMOUTER" } },
      -- A small bag: the same roots at two thirds of the size. Asked: the corner roots reach the bag's top and bottom
      -- edges, past them rather than short of them: each corner piece is moved out (6 up, 9 down) so its border root
      -- lies along the bag's edge and hangs past it. Both strips start and end 2 in, inside those border roots, which
      -- hide where they are cut. A frond.
      { Texture = "NightElfUnder", Point = "INNER", Width = 84, Tile = 336, X = -63, Start = 2, End = 2,
        Layer = "BACKGROUND", SubLevel = -2, Sizes = "Small" },
      { Texture = "NightElfRoots", Point = "INNER", Width = 84, Tile = 336, X = -63, Start = 2, End = 2,
        Sizes = "Small", SubLevel = 1 },
      { Texture = "NightElfCornerTop", Point = "TOPINNER", X = -63, Y = -6, Width = 84, Height = 42, SubLevel = 2,
        Sizes = "Small" },
      { Texture = "NightElfCornerBottom", Point = "BOTTOMINNER", X = -63, Y = 9, Width = 84, Height = 42, SubLevel = 2,
        Sizes = "Small" },
      { Texture = "NightElfFrond", Point = "TOPINNER", Anchor = "BOTTOMOUTER", X = -20, Y = 170, Width = 44,
        Height = 44, SubLevel = 3, Sizes = "Small", Motion = { Sway = 5, Period = 4.8, Origin = "BOTTOMOUTER" } },
    },
  },

  -- The roots are its flourish: no ribbon, cloud or shimmer by the title.
  Header = {
    TitleGlow = { Color = "Lavender", Alpha = 0.25 },
    Ribbon = false,
    Spark = false,
    Cloud = false,
  },

  -- Wisps: soft cyan-blue lights drifting slowly among the roots, steady, barely shrinking.
  Sparkles = {
    Texture = "Glow",
    Colors = { "Wisp", "WispLight", "Lavender" },
    TwinkleDepth = 0.15,
    Shrink = 0.15,
    Ribbon = false,
    Cloud = false,
    Edge = { Rate = 1.6, Max = 14, Life = { 4, 7 }, Size = { 8, 16 }, Speed = { 2, 7 }, Rise = { -4, 8 },
      Wobble = 10, Spin = 0, Alpha = 0.85, Reach = 110 },
  },

  Controls = {
    -- Round switches: a teal track when on, a lavender knob.
    Toggle = { Style = "Round", Width = 34, Height = 18, TrackHeight = 10, KnobSize = 16, HoverSpread = 5,
      On = { Color = "Gold", Alpha = 0.85 }, Knob = { Color = "Lavender" }, KnobOn = { Color = "White" } },
  },
})
