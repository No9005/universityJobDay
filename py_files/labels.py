def labels():
    f1_dict = {
        1: "männlich", 
        0: "weiblich", 
        2: "divers"}
    f2_dict = {
        0: "18 bis 20 Jahre", 
        1: "21 bis 25 Jahre", 
        2: "26 bis 30 Jahre", 
        3: "älter als 30 Jahre"}
    f3_dict = {
        0: "Wissenschaft", 
        1: "Medizin", 
        2: "Arbeit",
        3: "Privater Alltag", 
        4: "Shopping",
        5: "Öffentlicher Nahverkehr",
        6: "Sicherheit",
        7: "Finanzen",
        8: "Gesundheit & Fitness",
        9: "Anderer Bereich"}
    f4_dict = {
        0: "Uni",
        1: "Arbeit",
        2: "Medizin",
        3: "Privater Alltag",
        4: "Shopping",
        5: "Öffentlicher Nahverkehr",
        6: "Sicherheit",
        7: "Finanzen",
        8: "Gesundheit & Fitness"}
    f6_dict = {
        0: "benötigen mehr KI",
        1: "AI/KI nur Buzzwort",
        2: "Davon gibts schon genug!"}
    return [f1_dict, f2_dict, f3_dict, f4_dict, f6_dict]

def splits():
    return {
        "f1": ["f1", labels()[0]],
        "f2": ["f2", labels()[1]],
        "f6": ["f6", labels()[4]]
    }