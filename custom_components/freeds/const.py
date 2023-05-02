DOMAIN = "freeds"

# Working modes as defined for FW version 1.0.7

WORKING_MODES_1_0 = {
    0: None,
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

# Working modes as defined for FW version 1.1-beta

WORKING_MODES_1_1 = {
    0: None,
    1: "Solax Wifi v2 (ESP01)",
    2: "Solax Wifi v2 (local)",
    3: "Solax Wifi v1 (Hybrid)",
    4: "Meter DDS238-2(4)",
    5: "Meter DDSU666",
    6: "Meter SDM120/SDM220",
    7: "MQTT",
    8: "ICC Solar (MQTT)",
    9: "Shelly EM",
    10: "Shelly 3EM",
    11: "GoodWe ES/EM",
    12: "GoodWe EH",
    13: "Kostal Pico",
    14: "Wibeee",
    15: "Fronius API",
    16: "Fronius ModBus",
    17: "Victron",
    18: "SMA (Sunny boy)",
    19: "SMA (Sunny Island)",
    20: "Huawei",
    21: "Ingeteam",
    22: "SolarEdge",
    23: "FreeDS Slave",
    24: "Abb/Fimer Uno",
    25: "Schneider",
    26: "Wibeee ModBus",
    27: "MustSolar",
    28: "Solax (Chris Dongle)",
    29: "Huawei RTU",
    30: "Deye",
    31: "31",
    32: "32",
    33: "Fronius Gen 24 ModBus",
    34: "Solar Assistant (MQTT)",
    35: "Fox ESS",
    36: "Sofar Solar HYD",
}
