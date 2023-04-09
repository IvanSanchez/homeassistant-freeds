
DOMAIN = "freeds"

WORKING_MODES = {
    # ModBus RTU modes
    1: "DDS238",
    2: "DDSU666",
    3: "SDM Meter",
    4: "MustSolar",

    # HTTP API modes
    21: "Solax v2",
    22: "Solax v2 local",
    23: "Solax v1",
    24: "Wibeee",
    25: "Shelly EM",
    26: "Fronius",
    27: "FreeDS slave",
    28: "Goodwe",

    # MQTT modes
    41: "MQTT broker",
    42: "ICC solar",

    # ModBus TCP modes
    61: "SMA BOY",
    62: "VICTRON",
    63: "Fronius ModBus",
    64: "Huawei ModBus",
    65: "SMA island",
    66: "Schneider",
    67: "Wibeee ModBus",
    68: "Ingeteam",
    80: "SolarEdge",
}

