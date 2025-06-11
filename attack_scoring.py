from config import MARGINAL_THRESHOLDS

def compute_attack_scores(file_name):
    attack_scores = {}
    
    with open(file_name, 'rt') as attack_file:

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

if __name__=="__main__":
    # Example of usage

    print(compute_attack_scores('test.txt'))