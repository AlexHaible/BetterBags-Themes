import os
from PIL import Image

_T = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "textures")
CREST = os.path.join(_T, "DwarfCrest.png")

THEME = dict(
    Name="RacesDwarf", Background="MarbleBackground.png", BackgroundTileSize=128, BackgroundInset=8,
    Color=(0.85, 0.85, 1, 1), Slice=52, Outset=48, TitleY=40, Close={"X": 36, "Y": 36},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -42, "Y": 42},
    TabEdge=(0.38, 0.36, 0.36, 1), TabAccent=(0.72, 0.45, 0.2, 1),
)


def BORDER():
    return Image.open(os.path.join(_T, "DwarfBorder.png"))
