import json

ano_template = {
    "_ROOT_" : "Person",
#    Region  :  Sub-Region    
    "Person" : [
                 "Head",
                 "ArmR",
                 "HandR",
                 "ArmL",
                 "HandL",
                 "Chest",
                 "Hips",
                 "LegR",
                 "FootR",
                 "LegL",
                 "FootL",
               ],
    
#    Region  :  Trait (can be region)
    "Head"   : [ 
                 "Face",
                 "Hair",
                 "Hat",
               ],
    "Arm"    : [ ],
    "Hand"   : [ 
                 "Watch",
                 "Gloves",
               ],
    "Chest"  : [ ],
    "Hips"   : [ 
                 "Belt",
               ],
    "Leg"    : [ ],
    "Foot"   : [
                 "Socks",
                 "Shoes",
               ], 
    
    "_TAGS_" : {
#    Trait    : Nested Tags
    "Person"  : { "Clothing" : { "Business" : { "Suit"    : None,
                                                "Uniform" : None,
                                                "Dress"   : None, },
                                              
                                 "Casual"   : { "T-Shirt"    : None,
                                                "Chinos"     : None,
                                                "Skirt"      : None,
                                                "Athleasure" : None, 
                                                "VestTop"    : None, },
                                },
                                               
                  "#attributes" : { "Not-a-Robot" : None,
                                    "Woman"       : None,
                                    "Man"         : None,
                                  },
                },
                
    "Face"    : { # Things that miight confuse a classifier
                  "Glasses" : None,
                  "Makeup"  : { "Lipstick"   : None, 
                                "Eye-Makeup" : None, },
                },
    
    "Hair"   : { "#Colour" : { "Red"     : None,
                               "Brown"   : None,
                               "Blond"   : None,
                               "Black"   : None,
                               "Dyed"    : { "Red"    : None,
                                             "Blue"   : None,
                                             "Purple" : None, },
                               "Greying"    : None,
                             },
                 "Wet"     : None,
                 "Wig"     : None,
                 "Bald"    : None,
                },
                
    "Hat" : { "Fedora"         : None,
              "Bowler"         : None,
              "Baseball Cap"   : None, },
                      
    "Watch" : { "#Brand" : { "Swatch" : None,
                             "Casio"  : None,
                             "Omega"  : None, } ,
                "Mechanical" : None,
                "Analouge"   : None, },
                
                        
    "Gloves" : { "Regular"   : None,
                 "Fagin"     : None,
                 "Material"  : { "Wool"    : None,
                                 "Fabric"  : None,
                                 "Leather" : None, },
               },
                
    "Belt"  : { "Leather" : None,
                "Canvas"  : None, },

    "Socks"  : { "Comedy"  : None,
                 "Dark"    : None,
                 "Stripey" : None, },
    
    "Shoes" : { "Trainers" : None,
                "Boots"    : None,
                "Converse" : None,
                "Heels"    : None,
                "Dress"    : None, },
    } # Tags
} # Template

with open( "person_ano_tpl.json", "w" ) as fh:
    fh.write( json.dumps( ano_template, indent=2 ) )
    
