

# Circuit Constant
LCK, LPL, LEC, LTAN, LTAS, LCP = 'LCK', 'LPL', 'LEC', 'LTAN', 'LTAS', 'LCP'
WINTER, SPRING, SUMMER = 'Winter', 'Spring', 'Summer'
PLAYINS, MAINSTAGE, PLAYOFFS = 'PlayIns', 'MainStage', 'PlayOffs'
FIRSTSTAND, MSI, WORLDS = 'FirstStand', 'MSI', 'Worlds'


REGIONS = [LCK, LPL, LEC, LTAN, LTAS, LCP]
SPLITS = [WINTER, SPRING, SUMMER]
STAGES = [PLAYINS, MAINSTAGE, PLAYOFFS]
FINALS = [FIRSTSTAND, MSI, WORLDS]

EVENT_NAMING = "{region} {split} {year} {stage}"
STAGED_EVENT_NAMING = "{region} {split} {year} "


# Ranking Specificity
TEAM, LEAGUE = 'Team', 'League'
MODES = [TEAM, LEAGUE]
REGIONAL, INTERNATIONAL = 'Regional', 'International'
AUDIENCE = [REGIONAL, INTERNATIONAL]

AUDIENCE_MAPPING = {event: audience for audience,
                    events in zip(AUDIENCE, [REGIONS, FINALS])
                    for event in events}

IMPORTANCE = {REGIONAL: {stage: importance for stage,
                         importance in zip(STAGES, [8, 16, 20])},
              INTERNATIONAL: {stage: importance for stage,
                              importance in zip(STAGES, [12, 20, 36])},
              }

RANGES = {TEAM: 2,
          LEAGUE: 3}


'''
# GPR ELO IMPLEMENTATION CHECK
IMPORTANCE = {REGIONAL: {stage: importance for stage,
                         importance in zip(STAGES, [20, 20, 20])},
              INTERNATIONAL: {stage: importance for stage,
                              importance in zip(STAGES, [20, 20, 20])},
              }'''
