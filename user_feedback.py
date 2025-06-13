from config import WEIGHT_PARAMATER_ADJUST_AMOUNT
import json

#user_input is a dictionary that looks like {"name of tactic" : Bool} 
#where the bool is the user's input of whether the tactic happened
def update_weight_parameters(user_input):
    
    with open('weight_parameters.json','r') as file:
        
        thresholds = json.load(file)
        
        for tactic, input in user_input.items():
            if input:
                thresholds[tactic] += WEIGHT_PARAMATER_ADJUST_AMOUNT
            if not input:
                thresholds[tactic] += -WEIGHT_PARAMATER_ADJUST_AMOUNT
    
    with open('weight_parameters.json','w') as file:
        json.dump(thresholds, file)

#sample/test usage
if __name__ == "__main__":
    update_weight_parameters({"Exfiltration" : True, "Collection" : False})