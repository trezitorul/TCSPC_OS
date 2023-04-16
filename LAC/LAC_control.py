from LAC import LAC

def toUnit(value):
    return int(value * 1023)

def fromUnit(value):
    return value / 1023

class LAC_Feedback_Controlled:
    def __init__(self, retractLimit = 0.3, extendLimit = 0.73): #in current setup, change eventually
        self.lac = LAC()
        self.lac.set_extend_limit(toUnit(extendLimit))
        self.lac.set_retract_limit(toUnit(retractLimit))


    def get_feedback(self):
        return (fromUnit(self.lac.get_feedback))
        
    def set_position(self, value):
        if (value < 0.98 and value > 0.02):
            self.lac.set_position(toUnit(value))

    def reset(self):
        self.lac.reset()

#MAX: 2.97 @ 20mW power @0.3
#MIN: 0.29 @ 20mW powr @ 0.73