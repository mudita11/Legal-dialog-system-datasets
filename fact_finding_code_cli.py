import os
import subprocess
import numpy as np
import re
import json
import io
from itertools import product
from itertools import chain
# Update varibales before each full run: intent_list_to_test, single_turn

print("\n<><><><><><><><><><> Testing begins <><><><><><><><><><>")
main_test_utt = {
                ################################## Single-turn ###################################
                "info_test_utt" : ["i want to ask some general questions"], \
                "arrange_witness_test_utt" : ["can a beneficiary witness my will", "i do not have anyone available to witness my will can you help"], \
                "cost_test_utt" : ["Will there be any additional fees to your fee?", "what are the costs to your services if i am not entitled to legal aid?", "Is it free to amend a visa?", "How much do you charge for ​will amendments?", "how much do you charge to prepare a ​will?", "what are the costs for your services if i am not entitled to legal aid?", "what is the cost of making a ​will​ if i am not entitled to legal aid?", "do you deal with ​willa? How much do you charge?", "i need a cost estimate for legal proceedings.", "how much will it cost for you to act for me on a wildcard dispute?", "I have a dispute but need to know how much it will cost me before i instruct?", "How much will legal proceedings cost overall?"], \
                "slot_biz_sales_and_purchase" = ["I am buying an anything business. Can you help me?"], \
                "slot_contract_review" = ["can you help me with contract review?"], \
                "slot_draft_update_TnC" = ["can you draft me a contract?", "can you help me with my TnC?", "can you help me with my terms and conditions?", "i want to update my TnCs", "i want to update my terms and conditions", "i need my terms and conditions updating", "i need some new terms and conditions.", "can you draft me some terms and conditions?", ""], \
                "slot_employment" =
                "slot_NDA" =
                "slot_shareholders_agreement" =
                "slot_commercial_lease_landlord" =
                "slot_commercial_lease_tenant" =
                "slot_sell_comm_property" =
                "slot_buy_comm_property" =
                "slot_personal_injury" =
                ################################## Multi-turn ####################################
                "greet_test_utt" : ["hi", "hello", "hello there", "hey", "hiya", "hi there", "hey bot", "good morning", "good evening", "good afternoon", "morning"], \
                "touch_test_utt" : ["Get me in touch with a solicitor"], \
                ################################ Restart/Resume ##################################
                "session_restart" : [ "Restart the session", "restart session", "i would like to restart the session", "can i start the session again?", "start over", "can i restart the session", "i want to start over"], \
                "yes_no": ["yes"]
                }

utt_map_intent = {"greet_test_utt": "greet_intent",  "info_test_utt": "user_choice_to_general_info_intent", "touch_test_utt": "user_choice_to_contact_solicitor_intent", "cost_test_utt": "faq_cost_legalaid_intent", "arrange_witness_test_utt": "faq_arrange_witness_intent", "session_restart": "restart_session_intent", "yes_no": "not-an-intent"}

#intent_list_to_test = ["session_restart", "yes_no"]
intent_list_to_test = ["greet_test_utt", "touch_test_utt", ]#"greet_test_utt", "info_test_utt", "touch_test_utt"]
single_turn = False

correct_intent_names = []

if single_turn == True:
    ########################################### Faq (single-turn) ###########################################
    L = [(item,) for items in intent_list_to_test for item in chain(main_test_utt[items])]#; print(L) #; is equivalent to print(L, list(chain(zip(greet_test_utt)), zip(arrange_witness_test_utt)))
    [correct_intent_names.extend([*[[utt_map_intent[item]]]]*len(main_test_utt[item])) for item in intent_list_to_test]
else:
    ####################################### Fact finding (multi-turn) #######################################
    subdict_main = {item:main_test_utt[item] for item in intent_list_to_test}#; print(subdict)
    L = list(item for item in product(*subdict_main.values()))#; print("L--:",L)
    subdict_correct_intent = {item:[utt_map_intent[item]]*len(main_test_utt[item]) for item in intent_list_to_test}#; print(subdict_correct_intent)
    #print([[utt_map_intent[intent_list_to_test[0]]]]*len(main_test_utt[intent_list_to_test[0]]))
    correct_intent_names = list(item for item in product(*subdict_correct_intent.values()))
    
#print(L)

################################################ Writing ################################################
print("\n\n<><><><><><><><><><> Writing to a file <><><><><><><><><><>")

file_name = "intent_store.txt"
file = open(file_name, 'w')

count_conv = 0
for items in L:
    count_conv += 1
    file.write('\n\n**************** Conversation flow {} ****************'.format(count_conv))
    for item in items:
        print(items, item)
        cp = subprocess.run(args=['aws', 'lex-runtime', 'post-text', '--region', 'eu-west-1', '--bot-name', 'experiment_legal_bot', '--bot-alias', '$LATEST', '--user-id', 'msharma', '--input-text', item], capture_output=True) #print("before",cp.stdout.decode('utf-8')) # on command line: aws lex-runtime post-text --region eu-west-1 --bot-name experiment_legal_bot --bot-alias \$LATEST --user-id msharma --input-text "hi"
        out = json.loads(cp.stdout.decode('utf-8')); print(out,"\n")
        if item not in main_test_utt["yes_no"]:
            #file.write("\n==========> User input- {}\nIntent name- {}\nBot response- {}".format(item, out['sessionAttributes']['prev_intent'], out['message']))
            file.write("\n==========> User input- {}\nIntent name- {}\nBot response- {}".format(item, out['intentName'], out['message']))

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
conversation_score_count = 0
print("---------------------------------------------------------------------------------")
print("|Conversation flow | Number of intents | correctly identified intents | Result  |")
print("---------------------------------------------------------------------------------")
for sub_lists in zip(correct_intent_names, main_intent_list):
    #print("sub lists",sub_lists)
    conversation_flow_number += 1
    n_correct_intent = 0
    n_intents = 0
    for first, second in zip(sub_lists[0], sub_lists[1]):
        #print(sub_lists[0], sub_lists[1], first, second)
        n_intents += 1
        if first == second:
            n_correct_intent += 1
    if n_correct_intent == n_intents:
        pass_fail = "Pass"
    else:
        pass_fail = "Fail"
    print("| {} \t\t   | {} \t\t       | {} \t\t              | {} \t|".format(conversation_flow_number, n_intents, n_correct_intent, pass_fail))
print("---------------------------------------------------------------------------------")
#print("Test score is {}\n".format(score/len(correct_intent_names)))
print("\n\n<><><><><><><><><><> Testing is complete <><><><><><><><><><>\n")
