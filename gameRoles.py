gameRoles = {
    #passive & vanilla
    "Vanilla Town" : {
        "info" : "A vanilla town role. You have only your vote"
            },
    "Goon" : {
        "partner": True,
        "info" : "A Goon role."
            },
    "Mason" : {
        "partner": True,
        "info" : "At night, you and your mason partner may confer. You know that your mason partner is town."
            },
    "Godfather":{
        "partner": True,
        "info": "You are Reckoner"
        },

    #100 - copy
    #200 - hide
    #300 - bus
    #400 - block
    #500 - redirect
    #600 - Protect
    "Doctor" : {
        "info" : "At night, you may protect one target player from the Mafia kill.",
        "target" : 1
        },
    "Cop" : {
        "info" : "At night, you may investigate one target player and find out his alignment"
        }
}
