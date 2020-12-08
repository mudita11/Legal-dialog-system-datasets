import os
import subprocess
import numpy as np
import re
import json
import io
from itertools import product, chain
#from seen_data import utt_to_test, correct_intent_names
import random
import pyexcel
    
def write_file_(file, L, correct_intent_names):
    count_conv = 0
    for items in L:
        # next two statements are uncommented to test each button in fact finding
        print('\n\n**************** Session restarting ****************\n')
        file.write('\n\n**************** Session restarting ****************\n')
        # on command line: aws lex-runtime post-text --region eu-west-1 --bot-name Switch_Bots --bot-alias AlphaA --user-id msharma --input-text "hi"
        res = subprocess.run(args=['aws', 'lex-runtime', 'post-text', '--region', 'eu-west-1', '--bot-name', 'Switch_Bots', '--bot-alias', 'AlphaA', '--user-id', 'msharma', '--input-text', "restart"], capture_output=True); print(res)
        res_yes = subprocess.run(args=['aws', 'lex-runtime', 'post-text', '--region', 'eu-west-1', '--bot-name', 'Switch_Bots', '--bot-alias', 'AlphaA', '--user-id', 'msharma', '--input-text', "yes"], capture_output=True); print("\n",res_yes)
        
        file.write('\n\n**************** Conversation flow {} ****************'.format(count_conv+1))
        print('\n\n**************** Conversation flow {} ****************'.format(count_conv+1))
        
        correct_intent_names_index = 0
        for item in items:
            print("{} ==> {} ==> {}".format(items, item, correct_intent_names[count_conv][correct_intent_names_index]))
            file.write("{} ==> {} ==> {}".format(items, item, correct_intent_names[count_conv][correct_intent_names_index]))
            if item.startswith("++"):
                item = item[2:]
            cp = subprocess.run(args=['aws', 'lex-runtime', 'post-text', '--region', 'eu-west-1', '--bot-name', 'Switch_Bots', '--bot-alias', 'AlphaA', '--user-id', 'msharma', '--input-text', item], capture_output=True)#; print("item: {} cp: {} {}".format(item, cp, cp.stdout.decode('utf-8')))
            #print("json output {}".format(cp.stdout.decode('utf-8')))
            #file.write("json output {}".format(cp.stdout.decode('utf-8')))
            out = json.loads(cp.stdout.decode('utf-8'))
            print("\njson output: {}".format(out))
            file.write("\njson output: {}".format(out))
            if "intentName" in out:
                if out["intentName"] == "all_faq":
                    if "prev_intent" in out["sessionAttributes"]:
                        print("==========> User input- {}\nIdentified intent- {}\nCorrect intent- {}\nBot response- {}\n".format(item, out['sessionAttributes']['prev_intent'], correct_intent_names[count_conv][correct_intent_names_index], out['message']))
                        file.write("==========> User input- {}\nIdentified intent- {}\nCorrect intent- {}\nBot response- {}\n".format(item, out['sessionAttributes']['prev_intent'], correct_intent_names[count_conv][correct_intent_names_index], out['message']))
                else:
                    print("==========> User input- {}\nIdentified intent- {}\nCorrect intent- {}\nBot response- {}\n".format(item, out['intentName'], correct_intent_names[count_conv][correct_intent_names_index], out['message']))
                    file.write("==========> User input- {}\nIdentified intent- {}\nCorrect intent- {}\nBot response- {}\n".format(item, out['intentName'], correct_intent_names[count_conv][correct_intent_names_index], out['message']))
            else:
                print("==========> User input- {}\nIdentified intent- {}\nCorrect intent- {}\nBot response- {}\n".format(item, 'unrecognised', correct_intent_names[count_conv][correct_intent_names_index], out['message']))
                file.write("==========> User input- {}\nIdentified intent- {}\nCorrect intent- {}\nBot response- {}\n".format(item, 'unrecognised', correct_intent_names[count_conv][correct_intent_names_index], out['message']))
            correct_intent_names_index += 1
        count_conv += 1

def compile_identified_intent_(file_name):
    #Generation of intent list identified by lex
    main_identified_intent_list = []
    main_correct_intent_list = []
    identified_intent_list = []
    correct_intent_list = []
    with open(file_name, 'r') as file:
        for line in file:
            #print("line:", line)
            if "Conversation flow" in line and identified_intent_list != []:
                main_identified_intent_list.append(identified_intent_list)
                identified_intent_list = []
                main_correct_intent_list.append(correct_intent_list)
                correct_intent_list = []
            if "Identified intent" in line:
                split_intent = line.split()
                identified_intent_list.append(split_intent[2])
            if "Correct intent" in line:
                split_intent = line.split()
                correct_intent_list.append(split_intent[2])
        main_identified_intent_list.append(identified_intent_list)
        main_correct_intent_list.append(correct_intent_list)
    #print("Intents identified by lex: ", main_intent_list)
    return main_identified_intent_list, main_correct_intent_list

def test_log_(main_identified_intent_list, main_correct_intent_list):
    conversation_flow_number = 0
    pass_count = 0
    fail_count = 0
    print("---------------------------------------------------------------------------------")
    print("|Conversation flow | Number of intents | correctly identified intents | Result  |")
    print("---------------------------------------------------------------------------------")
    for sub_lists in zip(main_correct_intent_list, main_identified_intent_list):
        #print("sub lists",sub_lists)
        n_correct_intent = 0
        n_intents = 0
        for first, second in zip(sub_lists[0], sub_lists[1]):
            #print(sub_lists[0], sub_lists[1], first, second)
            n_intents += 1
            if first == second:
                n_correct_intent += 1
        if n_correct_intent == n_intents:
            pass_fail = "Pass"
            pass_count += 1
        else:
            pass_fail = "Fail"
            fail_count += 1
        print("| {} \t\t   | {} \t\t       | {} \t\t              | {} \t|".format(conversation_flow_number+1, n_intents, n_correct_intent, pass_fail))
        conversation_flow_number += 1
    print("---------------------------------------------------------------------------------")
    total_test_cases = pass_count + fail_count
    print("\n\n{} out of {} test cases passed with {}% score.".format(pass_count, total_test_cases, pass_count*100/total_test_cases))
    print("\n\n<><><><><><><><><><> Testing complete <><><><><><><><><><>\n")

def read_xlsx(file_name):
    data = pyexcel.get_book_dict(file_name=file_name); print(data.keys())
    faq_utt_to_test = [[cell for cell in row if cell !=''] for row in data['faq']]
    faq_utt_to_test = [row for row in faq_utt_to_test if row != []]
    
    faq_correct_intent_names = [[cell for cell in row if cell !=''] for row in data['faq_correct_intent']]
    faq_correct_intent_names = [row for row in faq_correct_intent_names if row != []]
    
    ff_utt_to_test = [[cell for cell in row if cell !=''] for row in data['ff']]
    ff_utt_to_test = [row for row in ff_utt_to_test if row != []]
    
    ff_correct_intent_names = [[cell for cell in row if cell !=''] for row in data['ff_correct_intent']]
    ff_correct_intent_names = [row for row in ff_correct_intent_names if row != []]
    
    restart_utt_to_test = [[cell for cell in row if cell !=''] for row in data['restart']]
    restart_utt_to_test = [row for row in restart_utt_to_test if row != []]
    
    restart_correct_intent_names = [[cell for cell in row if cell !=''] for row in data['restart_correct_intent']]
    restart_correct_intent_names = [row for row in restart_correct_intent_names if row != []]
    #print(faq_utt_to_test, "\n\n", faq_correct_intent_names, "\n\n", ff_utt_to_test, "\n\n", ff_correct_intent_names, "\n\n", restart_utt_to_test, "\n\n", restart_correct_intent_names)
    return faq_utt_to_test, faq_correct_intent_names, ff_utt_to_test, ff_correct_intent_names, restart_utt_to_test, restart_correct_intent_names

def main():
    file_name = "seen_data.xlsx"
    index_to_test = None
    faq_utt_to_test, faq_correct_intent_names, ff_utt_to_test, ff_correct_intent_names, restart_utt_to_test, restart_correct_intent_names = read_xlsx(file_name)
    #index_to_test = [3,4,5,7,8,14,17,18,21,30,42]#list(range(43))
    if index_to_test is not None:
        faq_utt_to_test = [faq_utt_to_test[item] for item in index_to_test]
        faq_correct_intent_names = [faq_correct_intent_names[item] for item in index_to_test]
        ff_utt_to_test = [ff_utt_to_test[item] for item in index_to_test]
        ff_correct_intent_names = [ff_correct_intent_names[item] for item in index_to_test]
        restart_utt_to_test = [restart_utt_to_test[item] for item in index_to_test]
        restart_correct_intent_names = [restart_correct_intent_names[item] for item in index_to_test]
    #print(faq_utt_to_test, faq_correct_intent_names)
    
    print("\n<><><><><><><><><><> Testing begins <><><><><><><><><><>")

    ################################################ Writing ################################################
    print("\n\n<><><><><><><><><><> Writing to a file <><><><><><><><><><>")

    file_name = "intent_store.txt"
    file = open(file_name, 'w')
    write_file_(file, faq_utt_to_test, faq_correct_intent_names)
    write_file_(file, ff_utt_to_test, ff_correct_intent_names)
    write_file_(file, restart_utt_to_test, restart_correct_intent_names)
    file.close()

    ######################################## Intent Identification Test ######################################
    print("\n\n<><><><><><><><><><> Test log <><><><><><><><><><>")
    main_identified_intent_list, main_correct_intent_list = compile_identified_intent_(file_name)
    #print(main_identified_intent_list, main_correct_intent_list)
    ################################################ Test Log ################################################
    test_log_(main_identified_intent_list, main_correct_intent_list)


if __name__ == "__main__":
    main()
