import os
from PIL import Image

_T = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "textures")
CREST = os.path.join(_T, "HumanCrest.png")

THEME = dict(
    Name="RacesHuman", Background="SOLID", BackgroundInset=8,
    Color=(0.01, 0.01, 0.2, 0.7), Slice=54, Outset=16, TitleY=24, Close={"X": 16, "Y": 16},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -24, "Y": 24},
    TabEdge=(0.26, 0.25, 0.22, 1), TabAccent=(0.85, 0.7, 0.25, 1),
)


def BORDER():
    return Image.open(os.path.join(_T, "HumanBorder.png"))
