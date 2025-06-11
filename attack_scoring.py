from config import MARGINAL_THRESHOLDS, DEFAULT_SCORES_PATH

def compute_attack_scores(file_name=DEFAULT_SCORES_PATH):
    attack_scores = dict()
    
    with open(file_name, 'rt') as attack_file:

        #Read each line of the file as a separate attack
        for line in attack_file:
            attack = line.strip().split(',')
            count = 0

            #Score the attack based on its marginals 
            for i in range(1, len(attack) - 2, 2):
                if float(attack[i + 1]) > MARGINAL_THRESHOLDS[attack[i]]:
                    count +=1
            
            attack_scores[attack[0]] = {"count": count, "score": attack[-1]}

    return attack_scores

if __name__ == "__main__":
    # Example of usage

    print(compute_attack_scores())