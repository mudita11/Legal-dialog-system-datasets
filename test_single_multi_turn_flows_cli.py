import os
import subprocess
import numpy as np
import re
import json
import io
from itertools import product
from itertools import chain
from data_file import main_test_utt, utt_map_intent

# Update varibales before each full run: intent_list_to_test, single_turn
#intent_list_to_test = ["session_restart", "slot_yes_no"]
#intent_list_to_test = ["greet_test_utt", "touch_test_utt", "slot_button_practicetype"]
intent_list_to_test = ["amend_will","appl_check_visa", "appl_check_visa", "appl_claim_length", "appointment_diff_office", "appointment_length", "arrange_witness_test_utt", "attend_meeting_someone", "boundary_neighbor_dispute", "CCJ", "copy_will", "cost_test_utt", "court_hearing_visa", "director_not_acting_properly", "disparaging_statement", "employment_tribunal", "expired_visa", "home_visit", "interpreter_visa", "legal_aid", "no_win_no_fee", "old_claim", "PI_MN", "prepare_appointment", "refusal_letter_visa", "settlement_agreement", "store_will", "user_owed_money_company", "user_owed_money", "validity_will", "faq_open_time", "biz_sales_and_purchase", "contract_review", "draft_update_TnC", "greet_test_utt"]
single_turn = True

print("\n<><><><><><><><><><> Testing begins <><><><><><><><><><>")

correct_intent_names = []

if single_turn == True:
    ########################################### Faq (single-turn) ###########################################
    L = [(item,) for items in intent_list_to_test for item in chain(main_test_utt[items])]#; print(L) #; is equivalent to print(L, list(chain(zip(greet_test_utt)), zip(arrange_witness_test_utt)))
    [correct_intent_names.extend([*[[utt_map_intent[item]]]]*len(main_test_utt[item])) for item in intent_list_to_test]
else:
    ####################################### Fact finding (multi-turn) #######################################
    subdict_main = {item:main_test_utt[item] for item in intent_list_to_test}#; print(subdict)
    L = list(item for item in product(*subdict_main.values()))#; print("L--:",L)
    subdict_correct_intent = {item:[utt_map_intent[item]]*len(main_test_utt[item]) for item in intent_list_to_test}
    #print([[utt_map_intent[intent_list_to_test[0]]]]*len(main_test_utt[intent_list_to_test[0]]))
    if "slot_button_practicetype" in subdict_correct_intent:
        subdict_correct_intent["slot_button_practicetype"] = ["get_details", "contract_review_intent", "draft_update_TnC_Contracts_intent", "Employment_contracts_intent", "Employment_policies_and_procedures_intent", "Employment_dispute_make_claim", "Employment_dispute_receive_claim", "Employment_settlement_agreement", "NDA", "SHD_incorporate_new_company", "SHD_incorporate_new_company", "SHD_incorporate_new_company", "SHD_incorporate_new_company", "Commercial_lease_acting_for_landlord", "Commercial_lease_acting_for_landlord", "Selling_commercial_property", "Buying_commercial_property", "Personal_injury"]
    print("correct sublist", subdict_correct_intent)
    correct_intent_names = list(item for item in product(*subdict_correct_intent.values()))

################################################ Writing ################################################
print("\n\n<><><><><><><><><><> Writing to a file <><><><><><><><><><>")

file_name = "intent_store.txt"
file = open(file_name, 'w')

count_conv = 0
for items in L:
    #subprocess.run(args=['aws', 'lex-runtime', 'post-text', '--region', 'eu-west-1', '--bot-name', 'experiment_legal_bot', '--bot-alias', '$LATEST', '--user-id', 'msharma', '--input-text', "restart session"], capture_output=False)
    #subprocess.run(args=['aws', 'lex-runtime', 'post-text', '--region', 'eu-west-1', '--bot-name', 'experiment_legal_bot', '--bot-alias', '$LATEST', '--user-id', 'msharma', '--input-text', "yes"], capture_output=False)
    file.write('\n\n**************** Conversation flow {} ****************'.format(count_conv))
    print('\n\n**************** Conversation flow {} ****************'.format(count_conv))
    for item in items:
        print(items, item)
        cp = subprocess.run(args=['aws', 'lex-runtime', 'post-text', '--region', 'eu-west-1', '--bot-name', 'experiment_legal_bot', '--bot-alias', '$LATEST', '--user-id', 'msharma', '--input-text', item], capture_output=True)#; print("before",cp.stdout.decode('utf-8')) # on command line: aws lex-runtime post-text --region eu-west-1 --bot-name experiment_legal_bot --bot-alias \$LATEST --user-id msharma --input-text "hi"
        out = json.loads(cp.stdout.decode('utf-8')); print(out,"\n")
        if item in main_test_utt["slot_yes_no"]:
            continue
        else:
            if "intentName" in out:
                file.write("\n==========> User input- {}\nIntent name- {}\nBot response- {}".format(item, out['intentName'], out['message']))
            else:
                file.write("\n==========> User input- {}\nIntent name- {}\nBot response- {}".format(item, out['sessionAttributes']['prev_intent'], out['message']))
    count_conv += 1

file.close()

################################################ Test log ################################################
print("\n\n<><><><><><><><><><> Test log <><><><><><><><><><>")

#Generation of intent list identified by lex
main_intent_list = []
intent_list = []
with open(file_name, 'r') as file:
    for line in file:
        #print("line:", line)
        if "Conversation flow" in line and intent_list != []:
            main_intent_list.append(intent_list)
            intent_list = []
        if "Intent name" in line:
            split_intent = line.split()
            intent_list.append(split_intent[2])
    main_intent_list.append(intent_list)
#print("Intents identified by lex: ", main_intent_list)

conversation_flow_number = 0
pass_count = 0
fail_count = 0
print("---------------------------------------------------------------------------------")
print("|Conversation flow | Number of intents | correctly identified intents | Result  |")
print("---------------------------------------------------------------------------------")
for sub_lists in zip(correct_intent_names, main_intent_list):
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
    conversation_flow_number += 1
    print("| {} \t\t   | {} \t\t       | {} \t\t              | {} \t|".format(conversation_flow_number, n_intents, n_correct_intent, pass_fail))
print("---------------------------------------------------------------------------------")
total_test_cases = pass_count + fail_count
print("\n\n{} out of {} test cases passed with {}% score.".format(pass_count, total_test_cases, pass_count*100/total_test_cases))
print("\n\n<><><><><><><><><><> Testing complete <><><><><><><><><><>\n")
