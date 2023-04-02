from LAC import LAC

def toUnit(value):
    return int(value * 1023)

def fromUnit(value):
    return value / 1023

class LAC:
    def __init__(self, retractLimit = 0.15, extendLimit = 0.98):
        self.lac = LAC()
        self.lac.set_extend_limit(toUnit(extendLimit))
        self.lac.set_retract_limit(toUnit(retractLimit))


    def get_feedback(self):
        return (fromUnit(self.lac.get_feedback))
        
    def set_position(self, value):
        self.lac.set_position(toUnit(value))

    def reset(self):
        self.lac.reset()
