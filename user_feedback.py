from config import MARGINAL_THRESHOLD_ADJUST_AMOUNT
import json

#woefully inefficient way to do this but it should work
def nudge_marginal_threshold(tactic, amount):
    with open('marginal_thresholds.json','r') as file:
        thresholds = json.load(file)
    thresholds[tactic] += amount
    with open('marginal_thresholds.json','w') as file:
        json.dump(thresholds, file)

#user_input is a dictionary that looks like {"name of tactic" : Bool} 
#where the bool is the user's input of whether the tactic happened
def update_marginal_thresholds(user_input):
    for tactic, input in user_input:
        if not input:
            nudge_marginal_threshold(tactic, -MARGINAL_THRESHOLD_ADJUST_AMOUNT)
                
        if input:
            nudge_marginal_threshold(tactic, MARGINAL_THRESHOLD_ADJUST_AMOUNT)