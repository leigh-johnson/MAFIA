gameRoles = {
    #passive & vanilla
    "Citizen" : {
        "info" : "You are an ordinary citizen, with no special powers or knowledge. You win when all threats to the Town are eliminated. ",
        'priority': 0,
            },
    "Goon" : {
        'priority': 0,
        "partner": True,
        "info" : "A Goon role.",
        "target": True,
            },
    "Mason" : {
        "partner": True,
        "info" : "You are a member of the Town masonry. You know that fellow masons are aligned with the Town. You win when all threats to the Town are eliminated. '"
            },
    "Godfather":{
        "target": True,
        'priority': 0,
        "partner": True,
        "info": "You are The Godfather, the big cheese in a small Mafia operation. You win when the Mafia controls this Town. "
        },

    #100 - copy
    #200 - hide
    #300 - bus
    #400 - block
    #500 - redirect
    #600 - Protect
    "Doctor" : {
        'target': True,
        'priority': 600,
        "info" : "You are a doctor, struggling to save lives in this doomed Town. At night, you may choose a target to be protected from Mafia assassination. You win when all threats to the town are eliminated"
        },
    #inspect
    "Macho Cop" : {
        "target": True,
        "priority": 700,
        "info": "At nightyou may investigate one target player and discover his alignment. If you are protected by a Doctor, your investigation will fail "},
    "Cop" : {
         "target": True,
        'priority': 700,
        "info" : "At night you may investigate one target player and discover his alignment"}
}
