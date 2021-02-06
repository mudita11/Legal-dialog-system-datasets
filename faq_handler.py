'''
hi -> general information (greet_options) -> <select service> (faq_reponse_per_intent) -> faq_reponse_per_intent

Thlambda function consists of two major parts: faq_single for intents applicable to a single service and faq|_multiple for intents applicable to multiple services.

faq_single function deals with returning the message for faq_single only
swi fucntion deals with returning the message for faq_multiple only

Special cases in faq_multiple: 
(1) cost intent- business sales and purchase does not require identifying 'business sales and purchase' slot value but needs to pick keywords such as business/property, sell/buy and based on the comnination of these keywords a slot value is assigned.
(2) intent faq_who_exe_bene_att is applicable to wills (attorney/beneciary) and LPA (attorney) services only and output is based on these three choices. 
(3) cost intent- once service is identified as LPA, the output depends on the follwed up options for single or couple.
'''
import logging
import boto3
import itertools as it

client = boto3.client('lex-runtime')
from faq_data_store import (buttons_exe_bene_att, buttons_practype_faq, intent_with_single_message_faq, buttons_single_couple,
                            faqpt_assignment_for_intent_with_single_message_faq, buttons_business_property, intent_with_multiple_message_faq, buttons_dispute_with,
                            buttons_practype_faq_store)
from fix_definitions import (get_slots, get_sessattr, get_userid, get_inputtranscript, close, elicit_slot, elicit_slot_without_button, elicit_intent_without_button, 
                                elicit_intent_without_message, elicit_intent, save_into_table_closing_remark, get_firstname, get_lastname, get_phonenumber, get_emailaddress, 
                                get_shdreason, get_contsort, get_companyname,  get_nofemployees, get_casedesc, get_claimagainst, get_accidenttime)
from fact_finding_data_store import (practice_list_map_intent, practice_list, personal_info, practice_map, intent_without_y_n_slot, intent_with_y_n_slot, intent_map_to_utt,
                                        full_intent_slot_message, full_slot_list)
dynamodb = boto3.resource('dynamodb', region_name = 'eu-west-1')
logger = logging.getLogger()
  
def identify_faq_index(sessattr, practice_list, ind):
    '''Assign service type index.'''
    if sessattr['practicetype'] in practice_map.keys():
        practise_type = practice_map[sessattr['practicetype']]
        sessattr['practicetype'] = practise_type
    if ind == None:
        ind = practice_list.index(sessattr['practicetype'].lower())
    sessattr['index_faq'] = ind
    return sessattr
        
str_to_function_name={'get_firstname': get_firstname, 'get_lastname': get_lastname, 'get_phonenumber': get_phonenumber, 'get_emailaddress': get_emailaddress}
    
def swi(intent_name, actual_intent_name, slots, sessattr, inputtext, intent_request, table):
    '''Return response to the user'''
    ind = sessattr['index_faq']
    if actual_intent_name == "faq_cost_legalaid_intent":
        if slots["contactdetails"] is None:
            if sessattr['practicetype'].lower() == "lasting power of attorney":
                if sessattr["singlecouple"].lower() == "single":
                    return elicit_slot_without_button(sessattr, "contact_details", slots, "contactdetails", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[actual_intent_name][ind][0]})
                if sessattr["singlecouple"].lower() == "couple":
                    return elicit_slot_without_button(sessattr, "contact_details", slots, "contactdetails", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[actual_intent_name][ind][1]})
            return elicit_slot_without_button(sessattr, "contact_details", slots, "contactdetails", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[actual_intent_name][ind]})
        elif slots["contactdetails"].lower() == "yes":
            for item in personal_info:
                if slots[item] is not None:
                    sessattr[item] = slots[item]
                elif item not in sessattr:
                    sessattr[item] = 'to_be_filled'
                    function_name = str_to_function_name['get_'+item]
                    return function_name(sessattr, "contact_details", slots, full_intent_slot_message["contact_details"][item])
                else:
                    slots[item] = inputtext
                    sessattr[item] = slots[item]
            slot_list = full_slot_list["contact_details"]
            if 'contactdetails' in sessattr:
                del sessattr['contactdetails']
            message1 = "Thank you. We have your contact details. Someone from the firm will contact you as soon as possible. You can find our contact details here https://www.fjg.co.uk/contact-us/colchester"
            message2 = "We have your contact details. One of the lawyers will be in touch soon. You can find our contact details here https://www.fjg.co.uk/contact-us/colchester"
            response = save_into_table_closing_remark(intent_request, table, sessattr, slots, slot_list, message1, message2)         
            return response
        elif slots['contactdetails'].lower() == 'no':
            if 'contactdetails' in sessattr:
                del ssessattr['contactdetails']
            return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": "No problem. You can find our contact details here https://www.fjg.co.uk/contact-us/colchester. What else would you like to know?"})
        else:
            return elicit_slot_without_button(sessattr, "contact_details", slots, "contactdetails", {"contentType": "PlainText", "content": "Please give a valid answer to the above question"})
    if actual_intent_name == 'faq_who_executer_beneficiary_attorney':
        if sessattr['exebeneatt'].lower() == 'executor':
            return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[actual_intent_name][ind][0]})
        if sessattr['exebeneatt'].lower() == 'beneficiary':
            return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[actual_intent_name][ind][1]})
    return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": intent_with_multiple_message_faq[actual_intent_name][ind]})    
    
    
def faq_single(sessattr, actual_intent_name):
    return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": intent_with_single_message_faq[actual_intent_name]})
    
    
def general_info(sessattr):
    return close(sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": "Sure, What would you like to know about "+sessattr['practicetype']+"?"})

child_bot_name = 'FAQ_legal'
child_bot_version = 'BetaA'
username = 'msharma'
response_posttext_fallback = "Sorry, I do not understand. Would you like to give your contact details for someone from the firm to contact you (Yes/No)?"
response_choices = "I can answer your queries in the following practices areas. Please select from these."

def posttext(bot_Name, bot_Alias, user_Id, input_Text, sessattr):
    response = boto3.client('lex-runtime').post_text(botName=bot_Name,
                                botAlias=bot_Alias,
                                userId=user_Id,
                                sessionAttributes=sessattr,
                                inputText=input_Text);
    return response
            
class response_per_intent():
    '''Handle faq use case to answer user queries in multiple services.'''
    def __init__(self, intent_request):
        '''Construct all the necessary attributes for the response_per_intent object.'''
        self.slots = get_slots(intent_request)
        self.intent_name = intent_request['currentIntent']['name']
        self.sessattr = get_sessattr(intent_request)
        if self.sessattr is None:
            self.sessattr = dict()
        self.inputtext = intent_request['inputTranscript']
        self.table = dynamodb.Table('user_data')
        self.ind = None
    
    def retrieve_faq_actual_intent_name(self):
        '''Retrieve answer from FAQ_legal bot using PostText call.'''
        actual_intent_name = None
        if self.intent_name == 'all_faq':
            if self.inputtext not in practice_list:
                response = posttext(child_bot_name, child_bot_version, username, self.inputtext, {})
                if 'intentName' in response:
                    actual_intent_name = response['intentName']
                    #set practicetype in switch_bots recognised by faq_legal bot
                    if 'practicetype' in response['sessionAttributes']:
                        self.sessattr['practicetype'] = response['sessionAttributes']['practicetype']
                elif response['message'] == 'Sorry, can you please repeat that?':
                    #if user text is not understood by the 'faq_legal 'bot
                    actual_intent_name = elicit_slot_without_button(
                                                self.sessattr,
                                                "contact_details",
                                                self.slots,
                                                "contactdetails",
                                                {"contentType": "PlainText",
                                                 "content": response_posttext_fallback
                                                 }
                    )
            else:
                actual_intent_name = self.sessattr['prev_intent']
        else:
            actual_intent_name = self.intent_name
        return actual_intent_name
        
    def resp_user_choice_general_info(self, actual_intent_name):
        '''Handle 'how about <service name>' kind of text.'''
        if actual_intent_name == 'user_choice_to_general_info_intent':
            if self.slots['practicetype'] is not None:
                if self.slots['practicetype'] in practice_map.keys():
                    self.slots['practicetype'] = practice_map[self.slots['practicetype']]
                self.sessattr['practicetype'] = self.slots['practicetype']
            if self.slots['practicetype'] == None and 'practicetype' not in self.sessattr:
                actual_intent_name = elicit_slot(
                                        self.sessattr,
                                        self.intent_name,
                                        self.slots,
                                        "practicetype",
                                        {"contentType": "PlainText",
                                         "content": response_choices},
                                         buttons_practype_faq
                )
            if 'practicetype' in self.sessattr:
                self.sessattr = identify_faq_index(self.sessattr, practice_list, self.ind)
                if self.sessattr['index_faq'] == 20:
                    if 'prev_intent' in self.sessattr:
                        del self.sessattr['prev_intent']
                    actual_intent_name = elicit_slot_without_button(self.sessattr, "contact_details", self.slots, "contactdetails", {"contentType": "PlainText", "content": "I can't help you with this service. But I can get you in touch with a solicitor to help you with your case. Would you like to give your contact details for someone from the firm to conatct you? (Yes/No)"})
                else:
                    if 'prev_intent' in self.sessattr:
                        if self.sessattr['prev_intent'] == 'contact_details':
                            actual_intent_name = 'faq_cost_legalaid_intent'
                        #following is added if user is in ff case and then says how about trusts?
                        elif self.sessattr['prev_intent'] in practice_list_map_intent.values():
                            actual_intent_name = general_info(self.sessattr)
                        else:
                            actual_intent_name = self.sessattr['prev_intent']
                    else:
                        actual_intent_name = general_info(self.sessattr)
                        #actual_intent_name = self.sessattr['prev_intent']
        return actual_intent_name
        
    def update_sessattr(self, actual_intent_name):
        '''Update history data.'''
        if actual_intent_name in faqpt_assignment_for_intent_with_single_message_faq.keys() or actual_intent_name in intent_with_multiple_message_faq.keys():
            self.sessattr['prev_intent'] = actual_intent_name
        if actual_intent_name == 'user_choice_to_contact_solicitor_intent' and 'practicetype' in self.sessattr:
            self.sessattr['prev_intent'] = practice_list_map_intent['practicetype']    
        if self.slots['practicetype'] is not None:
            self.sessattr['practicetype'] = self.slots['practicetype'] 
            self.sessattr = identify_faq_index(self.sessattr, practice_list, self.ind)
    
    def single_message_faq(self, actual_intent_name):
        '''Handle queries that are specific to a legal service.'''
        # intent name independent on the type of practicetype   
        if actual_intent_name in faqpt_assignment_for_intent_with_single_message_faq.keys():
            return faq_single(self.sessattr, actual_intent_name)
    
    def assign_ind_special_cases(self, actual_intent_name):
        '''Handle faq special cases applicable to multiple legal service.'''
        # assigns practicetype index for business sales and purchase, buying a biz property, selling a biz property within cost intent     
        if actual_intent_name == 'faq_cost_legalaid_intent' and self.slots['buysell'] is not None:
            if self.slots['proptype'] is None:
                return elicit_slot(self.sessattr, self.intent_name, self.slots, "proptype", {"contentType": "PlainText", "content": "Is it a business or property?"}, buttons_business_property)
            if self.slots['proptype'].lower() == 'business':
                self.sessattr['practicetype'] = 'business sales and purchase'
            if self.slots['proptype'].lower() == 'business property':
                if self.slots['buysell'] == "sell":
                    self.sessattr['practicetype'] = 'selling a commercial property'
                if self.slots['buysell'] == "buy":
                    self.sessattr['practicetype'] = 'buying a commercial property'
            self.sessattr = identify_faq_index(self.sessattr, practice_list, self.ind)
        
        if actual_intent_name == 'faq_who_executer_beneficiary_attorney':
            if self.slots['exebeneatt'] is not None:
                self.sessattr['exebeneatt'] = self.slots['exebeneatt']
            if self.slots['exebeneatt'] == None and 'exebeneatt' not in self.sessattr:
                return elicit_slot(self.sessattr, self.intent_name, self.slots, "exebeneatt", {"contentType": "PlainText", "content": "Please select from these."}, buttons_exe_bene_att)
            if self.sessattr['exebeneatt'].lower() in ['executor', 'beneficiary']:
                self.slots['practicetype'] = 'wills'
            if self.sessattr['exebeneatt'].lower() == 'attorney':
                self.slots['practicetype'] = 'lasting power of attorney'
            self.sessattr['practicetype'] = self.slots['practicetype']
            self.ind = practice_list.index(self.sessattr['practicetype'])
            self.sessattr = identify_faq_index(self.sessattr, practice_list, self.ind)
    
        # get practicetype
        if self.slots['practicetype'] is None and 'practicetype' not in self.sessattr:
            if actual_intent_name == "faq_store_will_intent":
                return elicit_slot(self.sessattr, self.intent_name, self.slots, "practicetype", {"contentType": "PlainText", "content": "I can answer your queries in the following practices areas. Please select from these."}, buttons_practype_faq_store)
            else:
                return elicit_slot(self.sessattr, self.intent_name, self.slots, "practicetype", {"contentType": "PlainText", "content": "I can answer your queries in the following practices areas. Please select from these."}, buttons_practype_faq)
        elif self.sessattr['practicetype'] is not None:
            #self.sessattr['practicetype'] = self.slots['practicetype']
            self.sessattr = identify_faq_index(self.sessattr, practice_list, self.ind)  
            if self.sessattr['index_faq'] == 20:
                #(1) 'prev_intent' is not recorded when 'practicetype' is 'any other' for the restart to function correctly after: what is the price? -> any other -> restart -> no
                if 'prev_intent' in self.sessattr:
                    del self.sessattr['prev_intent']
                return elicit_slot_without_button(self.sessattr, "contact_details", self.slots, "contactdetails", {"contentType": "PlainText", "content": "I can't help you with this service. But I can get you in touch with a solicitor to help you with your case. Would you like to give your contact details for someone from the firm to conatct you? (Yes/No)"})
            
        if actual_intent_name == "faq_cost_legalaid_intent":
            if self.sessattr['practicetype'].lower() == "lasting power of attorney":
                if self.slots["singlecouple"] == None:
                    return elicit_slot(self.sessattr, self.intent_name, self.slots, "singlecouple", {"contentType": "PlainText", "content": "Are you applying as a single person or a couple?"}, buttons_single_couple)
                self.sessattr['singlecouple'] = self.slots['singlecouple']    
                self.sessattr = identify_faq_index(self.sessattr, practice_list, self.ind)
    
    def multiple_message_faq(self, actual_intent_name, intent_request):
        '''Handle special cases for faq queries applicable to multiple legal service.'''
        resp = swi(self.intent_name, actual_intent_name, self.slots, self.sessattr, self.inputtext, intent_request, self.table)
        return resp
    
def lambda_handler(event, context):
    '''Create response_per_intent class objects and calls class methods.'''
    rpi = response_per_intent(event)
    actual_intent_name = rpi.retrieve_faq_actual_intent_name()
    if isinstance(actual_intent_name, dict):
        return actual_intent_name
    actual_intent_name = rpi.resp_user_choice_general_info(actual_intent_name)
    if isinstance(actual_intent_name, dict):
        return actual_intent_name
    rpi.update_sessattr(actual_intent_name)
    sing_mess = rpi.single_message_faq(actual_intent_name)
    if sing_mess is not None:
        return sing_mess
    ind_special = rpi.assign_ind_special_cases(actual_intent_name)
    if isinstance(ind_special, dict):
        return ind_special
    mult_mess = rpi.multiple_message_faq( actual_intent_name, event)
    if mult_mess is not None:
        return mult_mess
