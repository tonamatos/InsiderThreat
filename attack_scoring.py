DEFAULT_FILE_NAME = 'test.txt'
MARGINAL_THRESHOLDS = {
    "Initial Access" : 0.9,
    "Privilege Escalation" : 0.9,
    "Collection" : 0.9,
    "Exfiltration" : 0.9,
    "Defense Evasion" : 0.9
}

def compute_attack_scores(file):
    attack_scores = {}
    attack_file = open(file, 'rt')

    #Read each line of the file as a separate attack
    for line in attack_file:
        attack = line.split(',')
        score = 0

        #Score the attack based on its marginals 
        for i in range(1, len(attack), 2):
            if float(attack[i + 1]) > MARGINAL_THRESHOLDS[attack[i]]:
                score +=1
        
        attack_scores.update({attack[0] : score})

    return attack_scores

print(compute_attack_scores(DEFAULT_FILE_NAME))