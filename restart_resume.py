'''
This lambda function always asks if user wants to restart? If 'yes', history (sessattr) is deleted, 'no' has seven major parts:
(1) greet_intent, inform_bot_services_intent, greet_how_are_you_intent, ask_bot_name_intent
(2) user_choice_to_general_info
(3) user_choice_to_contact_solicitor
(4) faq_single
(5) faq_multiple: (a) intent faq_who_exe_bene_att is applicable to wills (attorney/beneciary) and LPA (attorney) services only and output is based on these three choices. 
                    (b) cost intent- once service is identified as LPA, the output depends on the follwed up options for single or couple.
(6) fact_finidng_without_y_n_resconv_no
(7) fact_finidng_with_y_n_resconv_no: special cases: commercial_lease_acting for landlord, if first slot to be filled is a button (slot_to_button_mapping.keys()), persoanl injury
'''
import logging
import itertools as it
from fact_finding_data_store import (full_slot_list, full_intent_slot_message, buttons_practype_fact_finding, buttons_practype_initial_options, commercial_private_lease_button,
                                            commercial_tenant_landlord_button, buttons_attorney_type, buttons_single_couple, practice_list, personal_info, intent_without_y_n_slot, 
                                            intent_with_y_n_slot, buttons_type_visa, slot_to_button_mapping, utt_map_to_intent, 
                                            practice_list_map_intent)
from fix_definitions import (get_slots, get_sessattr, get_userid, get_inputtranscript, close, elicit_slot, elicit_slot_without_button, elicit_intent, 
                            elicit_intent_without_button)
from faq_data_store import (faqpt_assignment_for_intent_with_single_message_faq, intent_with_single_message_faq, intent_with_multiple_message_faq, buttons_practype_faq, 
                            buttons_exe_bene_att)

logger = logging.getLogger()
                        
def faq_single(sessattr, intent_with_single_message_faq, switch_to_intent):
    return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": intent_with_single_message_faq[switch_to_intent]})

def faq_multiple(sessattr, intent_with_multiple_message_faq, switch_to_intent, slots):
    ind = int(sessattr['index_faq'])
    if switch_to_intent == 'faq_who_executer_beneficiary_attorney' and ind == 14:
        if sessattr['exebeneatt'].lower() == 'executor':
            return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[switch_to_intent][ind][0]})
        if sessattr['exebeneatt'].lower() == 'beneficiary':
            return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[switch_to_intent][ind][1]})
    if switch_to_intent == 'faq_cost_legalaid_intent':
        if ind == 15:
            if sessattr["singlecouple"].lower() == "single":
                return elicit_slot_without_button(sessattr, "contact_details", slots, "contactdetails", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[switch_to_intent][ind][0]})
            if sessattr["singlecouple"].lower() == "couple":
                return elicit_slot_without_button(sessattr, "contact_details", slots, "contactdetails", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[switch_to_intent][ind][1]})
        else:
            return elicit_slot_without_button(sessattr, "contact_details", slots, "contactdetails", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[switch_to_intent][ind]})            
    return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[switch_to_intent][ind]})
    
def general_info(sessattr):
    return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": "Sure, What would you like to know about "+sessattr['practicetype']+"?"})
    
def slot_not_filled_return(output_session_attributes):
    return elicit_intent(output_session_attributes, {"contentType": "PlainText", "content": "What else can I help you with today? Please select from these."}, 
                                                buttons_practype_initial_options)
                                                                            
def fact_finding_without_y_n_resconv_no(output_session_attributes, slots, switch_to_intent):
        #slots_not_filled = [item for item in full_slot_list[switch_to_intent] if item not in output_session_attributes.keys()]
        slots_not_filled = []
        if switch_to_intent == 'buy_sell_intent':
            lookup_slot_list = full_slot_list['buy_sell_intent'][practice_list_map_intent[output_session_attributes['practicetype'].lower()]]
            message = full_intent_slot_message['buy_sell_intent'][practice_list_map_intent[output_session_attributes['practicetype'].lower()]]
        else:
            lookup_slot_list = full_slot_list[switch_to_intent]
            message = full_intent_slot_message[switch_to_intent]
        for item in lookup_slot_list:
            if item not in output_session_attributes.keys():
                slots_not_filled.append(item)
            elif output_session_attributes[item] == 'to_be_filled':
                slots_not_filled.append(item)
        if slots_not_filled == []:
            return slot_not_filled_return(output_session_attributes)
        first_slot_to_be_filled = slots_not_filled[0]
        if first_slot_to_be_filled in slot_to_button_mapping.keys(): # ['attorneytype', 'singlecouple', 'type_visa']:
            return elicit_slot(output_session_attributes, switch_to_intent, slots, first_slot_to_be_filled, {"contentType": "PlainText", "content": \
                                message[first_slot_to_be_filled]}, slot_to_button_mapping[first_slot_to_be_filled])
        return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, first_slot_to_be_filled, {"contentType": "PlainText", "content": \
                                            message[first_slot_to_be_filled]})

def get_slots_not_filled(lookup_slot_list, plmi, output_session_attributes, suffix):
    slots_not_filled = []
    for item in lookup_slot_list[plmi+suffix]:
        if item not in output_session_attributes.keys():
            slots_not_filled.append(item)
        elif output_session_attributes[item] == 'to_be_filled':
            slots_not_filled.append(item)
    return slots_not_filled

def fact_finding_with_y_n_resconv_no(output_session_attributes, slots, switch_to_intent):
        if switch_to_intent == 'buy_sell_intent':
            plmi = practice_list_map_intent[output_session_attributes['practicetype'].lower()]
            lookup_slot_list = full_slot_list['buy_sell_intent']
            message = full_intent_slot_message['buy_sell_intent']
        else:
            plmi = switch_to_intent
            lookup_slot_list = full_slot_list
            message = full_intent_slot_message
        
        slot_y_n_choice = lookup_slot_list[plmi+'_1'][-1]
        if switch_to_intent == 'Personal_injury':
            if slot_y_n_choice not in output_session_attributes:
                return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slot_y_n_choice, {"contentType": "PlainText", "content": \
                                                    message[plmi+'_1'][slot_y_n_choice]})
            if output_session_attributes[slot_y_n_choice].lower() == 'yes': 
                slot_y_n_choice_1 = full_slot_list[plmi+'_1'][-2]
                if slot_y_n_choice_1 not in output_session_attributes:
                    return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slot_y_n_choice_1, {"contentType": "PlainText", "content": \
                                                        message[plmi+'_1'][slot_y_n_choice_1]})
                if output_session_attributes[slot_y_n_choice_1].lower() == 'yes':
                    slots_not_filled = get_slots_not_filled(lookup_slot_list, plmi, output_session_attributes, "_1")
                    if slots_not_filled == []:
                        return slot_not_filled_return(output_session_attributes)
                    return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slots_not_filled[0], {"contentType": "PlainText", "content": \
                                                        message[plmi+'_1'][slots_not_filled[0]]})
                elif output_session_attributes[slot_y_n_choice_1].lower() == 'no':
                    slots_not_filled = get_slots_not_filled(lookup_slot_list, plmi, output_session_attributes, "_2")
                    if slots_not_filled == []:
                        return slot_not_filled_return(output_session_attributes)
                    return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slots_not_filled[0], {"contentType": "PlainText", "content": \
                                                        message[plmi+'_2'][slots_not_filled[0]]})  
                else:
                    return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slot_y_n_choice_1, {"contentType": "PlainText", "content": \
                                                        "Please gice a valid answer."})
            elif output_session_attributes[slot_y_n_choice].lower() == 'no':
                slot_y_n_choice_3 = full_slot_list[plmi+'_3'][-1]
                if slot_y_n_choice_3 not in output_session_attributes:
                    return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slot_y_n_choice_3, {"contentType": "PlainText", "content": \
                                                        message[plmi+'_3'][slot_y_n_choice_3]})
                if output_session_attributes[slot_y_n_choice_3].lower() == 'yes':                        
                    slots_not_filled = get_slots_not_filled(lookup_slot_list, plmi, output_session_attributes, "_3")
                    if slots_not_filled == []:
                        return slot_not_filled_return(output_session_attributes)
                    return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slots_not_filled[0], {"contentType": "PlainText", "content": \
                                                        message[plmi+'_1'][slots_not_filled[0]]})
                elif output_session_attributes[slot_y_n_choice_3].lower() == 'no':
                    slots_not_filled = get_slots_not_filled(lookup_slot_list, plmi, output_session_attributes, "_4")
                    if slots_not_filled == []:
                        return slot_not_filled_return(output_session_attributes)
                    return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slots_not_filled[0], {"contentType": "PlainText", "content": \
                                                        message[plmi+'_4'][slots_not_filled[0]]})
                else:
                    return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slot_y_n_choice_3, {"contentType": "PlainText", "content": \
                                                        "Please give a valid answer."})
            else:
                return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slot_y_n_choice, {"contentType": "PlainText", "content": \
                                                    "Please give a valid answer."})
        else:    
            if slot_y_n_choice not in output_session_attributes:
                if switch_to_intent == 'Commercial_lease_acting_for_landlord':
                    if 'tenant_landlord' not in output_session_attributes:
                        return elicit_slot(output_session_attributes, switch_to_intent, slots, 'tenant_landlord', {"contentType": "PlainText", "content": \
                                                    message[plmi+'_1']['tenant_landlord']}, commercial_tenant_landlord_button)
                    elif output_session_attributes['tenant_landlord'].lower() == 'landlord':
                        return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slot_y_n_choice, {"contentType": "PlainText", "content": \
                                                    message[plmi+'_1'][slot_y_n_choice+'_1']})
                    elif output_session_attributes['tenant_landlord'].lower() == 'tenant':
                        return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slot_y_n_choice, {"contentType": "PlainText", "content": \
                                                    message[plmi+'_1'][slot_y_n_choice+'_2']})
                return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slot_y_n_choice, {"contentType": "PlainText", "content": \
                                                    message[plmi+'_1'][slot_y_n_choice]})
            if output_session_attributes[slot_y_n_choice].lower() == 'yes':
                slots_not_filled = get_slots_not_filled(lookup_slot_list, plmi, output_session_attributes, "_1")
                if slots_not_filled == []:
                    return slot_not_filled_return(output_session_attributes)
                first_slot_to_be_filled = slots_not_filled[0]  
                if first_slot_to_be_filled in slot_to_button_mapping.keys(): # ['attorneytype', 'singlecouple', 'type_visa']:
                    return elicit_slot(output_session_attributes, switch_to_intent, slots, first_slot_to_be_filled, {"contentType": "PlainText", "content": \
                                        message[plmi+'_1'][first_slot_to_be_filled]}, slot_to_button_mapping[first_slot_to_be_filled])
                return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, first_slot_to_be_filled, {"contentType": "PlainText", "content": \
                                                  message[plmi+'_1'][first_slot_to_be_filled]})
            elif output_session_attributes[slot_y_n_choice].lower() == 'no':
                slots_not_filled = get_slots_not_filled(lookup_slot_list, plmi, output_session_attributes, "_2")
                if slots_not_filled == []:
                    return slot_not_filled_return(output_session_attributes)
                first_slot_to_be_filled = slots_not_filled[0]    
                if first_slot_to_be_filled in slot_to_button_mapping.keys(): # ['attorneytype', 'singlecouple', 'type_visa']:
                    return elicit_slot(output_session_attributes, switch_to_intent, slots, first_slot_to_be_filled, {"contentType": "PlainText", "content": \
                                        message[plmi+'_2'][first_slot_to_be_filled]}, slot_to_button_mapping[first_slot_to_be_filled])
                return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, first_slot_to_be_filled, {"contentType": "PlainText", "content": \
                                                    message[plmi+'_2'][first_slot_to_be_filled]})
            else:
                return elicit_slot_without_button(output_session_attributes, switch_to_intent, slots, slot_y_n_choice, {"contentType": "PlainText", "content": \
                                                    "Please give a valid answer."})

    
def elicit_intent_initial_options(sessattr, message):
    return elicit_intent(sessattr, {"contentType": "PlainText", "content": message}, buttons_practype_initial_options)


class response_per_intent():
    def __init__(self, intent_request):
        self.slots = get_slots(intent_request)
        self.intent_name = intent_request['currentIntent']['name']
        self.sessattr = get_sessattr(intent_request) #returns {} in lex test console and None in slack
        if self.sessattr is None:
            self.sessattr = dict()
    
    def startover_response_per_intent(self):
        if self.intent_name == 'startover_intent':
            return elicit_slot_without_button(self.sessattr, 'restart_session_intent', self.slots, "resconv", {"contentType": "PlainText", "content": "Are you sure you want to restart? (Yes/No)"})
            
    def response_per_resconv(self):
        if self.slots['resconv'] is None:
            if self.intent_name == "out_of_intent":
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "resconv", {"contentType": "PlainText", "content": "I think we are having trouble with the conversation. Do \
                                                you want to restart? (Yes/No)"})
            elif self.intent_name == "restart_session_intent":
                return elicit_slot_without_button(self.sessattr, "restart_session_intent", self.slots, "resconv", {"contentType": "PlainText", "content": "Are you sure you want to restart? (Yes/No)"})
    
        if self.slots['resconv'].lower() == 'yes':
            self.sessattr = {}
            return elicit_intent_initial_options(self.sessattr, "Your session has been restarted. I can assist you with the following services today. Please select from these.")
    
        if self.slots['resconv'].lower() == 'no':
            if 'prev_intent' in self.sessattr:
                switch_to_intent = self.sessattr['prev_intent']
                all_faq_intents = list(it.chain(intent_with_single_message_faq.keys(), intent_with_multiple_message_faq.keys()))
                if switch_to_intent == "contact_details":
                    #'contactdetails' not in sessattr means that user has given the conatct details or user has said 'no' to recording conatct details. 
                    if 'contactdetails' not in self.sessattr:
                        #hi -> i want to speak to a solicitor -> any other -> sam -> sam -> 234 -> sam-sam -> casedesc. -> restart -> no
                        #justice -> justice -> yes -> sam -> jan -> 123 -> sam-jan -> casedesc. -> restart -> no
                        if 'firstname' in self.sessattr:
                            return elicit_intent_without_button(self.sessattr, {"contentType": "PlainText", "content": "Thank you. We have your contact details. Someone from the firm \
                                will contact you as soon as possible. You can find our contact details here https://www.fjg.co.uk/contact-us/colchester"})
                        else:
                            #hi -> i want to speak to a solicitor -> any other -> no -> restart -> no
                            #justice -> justice -> no -> restart -> no
                            #what is the price -> employment contract -> no -> restart -> no
                            return elicit_intent_without_button(self.sessattr, {"contentType": "PlainText", "content": "No problem. You can find our contact details here \
                                https://www.fjg.co.uk/contact-us/colchester. What else would you like to know?"})
                    else:
                        #hi -> i want to speak to a solicitor -> any other -> sam -> restart -> no
                        #justice -> justice -> yes -> sam -> restart -> no
                        if self.sessattr['contactdetails'].lower() == 'yes':
                            lookup_slot_list = full_slot_list
                            plmi = switch_to_intent
                            suffix = ''
                            slots_not_filled = get_slots_not_filled(lookup_slot_list, plmi, self.sessattr, suffix)
                            if slots_not_filled == []:
                                return slot_not_filled_return(output_session_attributes)
                            first_slot_to_be_filled = slots_not_filled[0]    
                            return elicit_slot_without_button(self.sessattr, switch_to_intent, self.slots, first_slot_to_be_filled, {"contentType": "PlainText", "content": \
                                full_intent_slot_message['contact_details'][first_slot_to_be_filled]})
                    
                # in response to: "justice" -> justice -> restart -> no
                if switch_to_intent == "fallback_intent":
                    return elicit_slot_without_button(self.sessattr, "contact_details", self.slots, "contactdetails", {"contentType": "PlainText", "content": "I would need your contact details for someone from the firm to contact you. Are you happy to give your contact \
                        details? (Yes/No)"})
                
                ################----------------fact-finding-without-y-n-slot---------------################
                if switch_to_intent == 'buy_sell_intent':
                    if self.sessattr['practicetype'].lower() == 'business sales and purchase':
                        return fact_finding_without_y_n_resconv_no(self.sessattr, self.slots, switch_to_intent)
                    else:
                        return fact_finding_with_y_n_resconv_no(self.sessattr, self.slots, switch_to_intent)
                    
                elif switch_to_intent in intent_without_y_n_slot:
                    return fact_finding_without_y_n_resconv_no(self.sessattr, self.slots, switch_to_intent)
                
                ################----------------fact-finding-with-y-n-slot---------------################
                elif switch_to_intent in intent_with_y_n_slot:
                    return fact_finding_with_y_n_resconv_no(self.sessattr, self.slots, switch_to_intent)
                    
                elif switch_to_intent in all_faq_intents:
                    ################----------------faq-single---------------################
                    if switch_to_intent in intent_with_single_message_faq.keys():
                        return faq_single(self.sessattr, intent_with_single_message_faq, switch_to_intent)
                
                    ################----------------faq-multiple---------------################
                    if switch_to_intent in intent_with_multiple_message_faq.keys():
                        if switch_to_intent == "faq_who_executer_beneficiary_attorney":
                            if 'exebeneatt' not in self.sessattr:
                                return elicit_slot(self.sessattr, "all_faq", self.slots, "exebeneatt", {"contentType": "PlainText", "content": "Please select from these."}, buttons_exe_bene_att)
                        if 'practicetype' in self.sessattr:
                            if switch_to_intent == "faq_cost_legalaid_intent" and int(self.sessattr['index_faq']) == 15:
                                if 'singlecouple' not in self. sessattr: 
                                    return elicit_slot(self.sessattr, "all_faq", self.slots, "singlecouple", {"contentType": "PlainText", "content": "Are you applying as a single person or a couple?"}, buttons_single_couple)                
                        else: 
                            return elicit_slot(self.sessattr, "all_faq", self.slots, "practicetype", {"contentType": "PlainText", "content": "I can answer your queries in the following practices \
                                                areas. Please select from these."}, buttons_practype_faq)
                        return faq_multiple(self.sessattr, intent_with_multiple_message_faq, switch_to_intent, self.slots)
            elif 'practicetype' in self.sessattr:
                if self.sessattr['practicetype'].lower() == 'any other':
                    #ff case: hi -> i want to speak to a solicitor -> any other -> restart -> no
                    #faq case: what is the price? -> any other -> restart -> no
                    return elicit_slot_without_button(self.sessattr, "contact_details", self.slots, "contactdetails", {"contentType": "PlainText", "content": "I can't help you with this service. But I can get you in touch with a \
                        solicitor to help you with your case. Would you like to give your contact details for some form the firm to conatct you? (Yes/No)"})
                return general_info(self.sessattr)
            else:
                return elicit_intent(self.sessattr, {"contentType": "PlainText", "content": "Your session has been resumed. I can assist you with the following services today. Please \
                                        select from these."}, buttons_practype_initial_options)

    
def lambda_handler(event, context):
    rpi = response_per_intent(event)
    startover_response = rpi.startover_response_per_intent()
    if startover_response is not None:
        return startover_response
    return rpi.response_per_resconv()

