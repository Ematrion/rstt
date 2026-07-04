from enum import StrEnum


class Region(StrEnum):
    LCK     = "LCK"
    LPL     = "LPL"
    LEC     = "LEC"
    LTAN    = "LTAN"
    LTAS    = "LTAS"
    LCP     = "LCP"


class Split(StrEnum):
    Winter  = "Winter"
    Spring  = "Spring"
    Summer  = "Summer"


class Stage(StrEnum):
    PlayIns         = "PlayIns"
    MainStage       = "MainStage"
    PlayOffs        = "PlayOffs"


class Finals(StrEnum):
    FirstStand      = "FirstStand"
    MSI             = "MSI"
    Worlds          = "Worlds"


class Role(StrEnum):
    Toplaner        = "Toplaner"
    Jungle          = "Jungler"
    Midlaner        = "Midlaner"
    Botlaner        = "Botlaner"
    Support         = "Support"


class Audience(StrEnum):
    Regional        = "Regional"
    International   = "International"
    
    
EVENT_AUDIENCE = {event: audience for audience,
                    events in zip(Audience, [Region, Finals])
                    for event in events}