from enum import StrEnum


class Region(StrEnum):
    LCK = "LCK"
    LPL = "LPL"
    LEC = "LEC"
    LTAN = "LTAN"
    LTAS = "LTAS"
    LCP = "LCP"


class Split(StrEnum):
    Winter = "Winter"
    Spring = "Spring"
    Summer = "Summer"


class Finals(StrEnum):
    FirstStand = "FirstStand"
    MSI = "MSI"
    Worlds = "Worlds"


class Stages(StrEnum):
    PlayIns = "PlayIns"
    MainStage = "MainStage"
    PlayOffs = "PlayOffs"


class Role(StrEnum):
    Toplaner = "Toplaner"
    Jungle = "Jungler"
    Midlaner = "Midlaner"
    Botlaner = "Botlaner"
    Support = "Support"
