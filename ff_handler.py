import boto3
import os
import datetime
import botocore.session
import itertools as it
from fact_finding_data_store import (full_intent_slot_message, full_slot_list, commercial_private_lease_button, practice_list, personal_info, intent_without_y_n_slot, intent_with_y_n_slot,
                           commercial_tenant_landlord_button, buttons_attorney_type, buttons_single_couple, buttons_type_visa, buttons_shareholders_agreement, intent_map_to_utt)
from fix_definitions import (get_slots, get_userid, get_inputtranscript, get_sessattr, close, elicit_slot_without_button, elicit_slot, confirm_intent, elicit_intent, 
                                get_firstname, get_lastname, get_phonenumber, get_emailaddress, get_shdreason, get_contsort, get_companyname, get_nofemployees, get_casedesc, 
                                get_claimagainst, get_accidenttime, save_into_table_closing_remark)
from faq_data_store import intent_with_single_message_faq, intent_with_multiple_message_faq

region = os.environ.get('AWS_DEFAULT_REGION', 'eu-west-1')

dynamodb = boto3.resource('dynamodb', region_name = 'eu-west-1')

def posttext(bot_Name, bot_Alias, user_Id, input_Text):
    response = boto3.client('lex-runtime').post_text(botName=bot_Name,
                                botAlias=bot_Alias,
                                userId=user_Id,
                                sessionAttributes={},
                                inputText=input_Text);
    return response

    
class response_per_intent():
    def __init__(self, intent_request):
        self.slots = get_slots(intent_request)
        self.InputText = intent_request['inputTranscript']
        self.intent_name = intent_request['currentIntent']['name']
        self.table = dynamodb.Table('user_data')
        self.sessattr = get_sessattr(intent_request)
        if self.sessattr is None:
            self.sessattr = dict()
        self.sessattr['prev_intent'] = self.intent_name
    
    def create_dynamodb_table(self):
        self.table = dynamodb.create_table(
                TableName = 'user_data',
                KeySchema = [
                                {'AttributeName' :   'user_ID', 'KeyType'   :   'HASH'},
                                {'AttributeName' :   'practicetype', 'KeyType'   :   'RANGE'},
                            ],
                AttributeDefinitions = [
                                        {'AttributeName' : 'user_ID', 'AttributeType' :   'S'},
                                        {'AttributeName' :   'practicetype', 'AttributeType' :   'S'},
                                        ],
                ProvisionedThroughput={'ReadCapacityUnits': 3, 'WriteCapacityUnits': 3}
                )
    
    def find_slot_in_y_n_intent_slot(self):
        if self.intent_name not in intent_without_y_n_slot and self.intent_name != 'buy_sell_intent':
            slot_y_n_choices = full_slot_list[self.intent_name+'_1'][-1]
        else:
            slot_y_n_choices = None
        return slot_y_n_choices

    def ff_questions(self, slot_y_n_choices, intent_request):
        str_to_function_name={'get_firstname': get_firstname, 'get_lastname': get_lastname, 'get_phonenumber': get_phonenumber, 'get_emailaddress': get_emailaddress}
        #-----------------------------------Fallback-------------------------------------------
        if self.intent_name == 'fallback_intent':
            return elicit_slot_without_button(self.sessattr, "contact_details", self.slots, "contactdetails", {"contentType": "PlainText", "content": full_intent_slot_message["contact_details"]["contactdetails"]})
                    
        if self.intent_name == 'contact_details':
            if self.slots['contactdetails'] is None and 'contactdetails' not in self.sessattr:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "contactdetails", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name]["contactdetails"]})
            if self.slots['contactdetails'] is not None: 
                self.sessattr['contactdetails'] = self.slots['contactdetails']
            if self.sessattr['contactdetails'].lower() == 'no':
                del self.sessattr['contactdetails']
                return close(self.sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": "No problem. You can find our contact details here https://www.fjg.co.uk/contact-us/colchester. What else would you like to know?"})
            elif self.sessattr['contactdetails'].lower() == 'yes':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name][item])
                    else:
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'casedesc' not in self.sessattr:
                    self.sessattr['casedesc'] = 'to_be_filled'
                    return get_casedesc(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name]['casedesc'])
                if self.sessattr['casedesc'] == 'to_be_filled':
                    self.slots['casedesc'] = self.InputText
                    self.sessattr['casedesc'] = self.slots['casedesc']
                slot_list = full_slot_list[self.intent_name]
                del self.sessattr['contactdetails']
                message1 = "Thank you. We have your contact details. Someone from the firm will contact you as soon as possible. You can find our contact details here https://www.fjg.co.uk/contact-us/colchester"
                message2 = "We have your contact details. One of the lawyers will be in touch soon. You can find our contact details at https://www.fjg.co.uk/contact-us/colchester"
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "contactdetails", {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                
        #-----------------------------------Commercial corporate-------------------------------------------
        if self.intent_name == 'buy_sell_intent':
            if 'practicetype' not in self.sessattr:
                if self.slots['proptype'] is None:
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "proptype", {"contentType": "PlainText", "content": "Is its a business or a property?"})
                if self.slots['proptype'] == 'business':
                    key_name = "get_details" 
                if self.slots['proptype'] == 'business property':
                    if self.slots['buysell'] == None:
                        return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "buysell", {"contentType": "PlainText", "content": "Are you buying or selling?"})
                    if self.slots['buysell'] == 'sell':
                        key_name = "Selling_commercial_property"
                        slot_y_n_choices = 'termsofsale'
                    if self.slots['buysell'] == 'buy':
                        key_name = "Buying_commercial_property"
                        slot_y_n_choices = 'termsofpurchase'
            else:
                if self.sessattr['practicetype'].lower() == 'business sales and purchase':
                    key_name = "get_details"
                if self.sessattr['practicetype'].lower() == 'selling a commercial property':
                    key_name = "Selling_commercial_property"
                    slot_y_n_choices = 'termsofsale'
                if self.sessattr['practicetype'].lower() == 'buying a commercial property':
                    key_name = "Buying_commercial_property"
                    slot_y_n_choices = 'termsofpurchase'
                        
            if key_name == "Selling_commercial_property":
                self.sessattr['practicetype'] = practice_list[11]
                if self.slots[slot_y_n_choices] == None and slot_y_n_choices not in self.sessattr:
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message['buy_sell_intent'][key_name+'_1'][slot_y_n_choices]})
                if self.slots[slot_y_n_choices] is not None:
                    self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
                if self.sessattr[slot_y_n_choices].lower() == 'yes':
                    for item in personal_info:
                        if self.slots[item] is not None:
                            self.sessattr[item] = self.slots[item]
                        elif item not in self.sessattr:
                            self.sessattr[item] = 'to_be_filled'
                            function_name = str_to_function_name['get_'+item]
                            return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message['buy_sell_intent'][key_name+'_1'][item])
                        elif self.sessattr[item] == 'to_be_filled':
                            self.slots[item] = self.InputText
                            self.sessattr[item] = self.slots[item]
                    slot_list = full_slot_list['buy_sell_intent'][key_name+'_1']
                    message1 = "Thank you. We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                    message2 = "We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                elif self.sessattr[slot_y_n_choices].lower() == 'no':
                    for item in personal_info:
                        if self.slots[item] is not None:
                            self.sessattr[item] = self.slots[item]
                        elif item not in self.sessattr:
                            self.sessattr[item] = 'to_be_filled'
                            function_name = str_to_function_name['get_'+item]
                            return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message['buy_sell_intent'][key_name+'_2'][item])
                        elif self.sessattr[item] == 'to_be_filled':
                            self.slots[item] = self.InputText
                            self.sessattr[item] = self.slots[item]
                    slot_list = full_slot_list['buy_sell_intent'][key_name+'_2']
                    message1 = "Thank you. We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                    message2 = "We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                else:
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                
            if key_name == "Buying_commercial_property":
                self.sessattr['practicetype'] = practice_list[12]
                if self.slots[slot_y_n_choices] == None and slot_y_n_choices not in self.sessattr:
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message['buy_sell_intent'][key_name+'_1'][slot_y_n_choices]})
                if self.slots[slot_y_n_choices] is not None:
                    self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
                if self.sessattr[slot_y_n_choices].lower() == 'yes':
                    for item in personal_info:
                        if self.slots[item] is not None:
                            self.sessattr[item] = self.slots[item]
                        elif item not in self.sessattr:
                            self.sessattr[item] = 'to_be_filled'
                            function_name = str_to_function_name['get_'+item]
                            return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message['buy_sell_intent'][key_name+'_1'][item])
                        elif self.sessattr[item] == 'to_be_filled':
                            self.slots[item] = self.InputText
                            self.sessattr[item] = self.slots[item]
                    slot_list = full_slot_list['buy_sell_intent'][key_name+'_1']
                    message1 = "Thank you. We have your contact details. Someone from the firm will contact you Thank you for contacting Fisher Jones Greenwood Solicitors."
                    message2 = "We have your contact details. Someone from the firm will contact you Thank you for contacting Fisher Jones Greenwood Solicitors."
                elif self.sessattr[slot_y_n_choices].lower() == 'no':
                    for item in personal_info:
                        if self.slots[item] is not None:
                            self.sessattr[item] = self.slots[item]
                        elif item not in self.sessattr:
                            self.sessattr[item] = 'to_be_filled'
                            function_name = str_to_function_name['get_'+item]
                            return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message['buy_sell_intent'][key_name+'_2'][item])
                        elif self.sessattr[item] == 'to_be_filled':
                            self.slots[item] = self.InputText
                            self.sessattr[item] = self.slots[item]
                    slot_list = full_slot_list['buy_sell_intent'][key_name+'_2']
                    message1 = "Thank you. We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                    message2 = "We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                else:
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                    
            if key_name == "get_details":
                self.sessattr['practicetype'] = practice_list[0]
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message['buy_sell_intent'][key_name][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                slot_list = full_slot_list['buy_sell_intent'][key_name]
                message1 = "Thank you for that. We have your contact details. One of our lawyers will be in touch soon. I am now transferring you to some further information which I hope you will find useful. https://www.fjg.co.uk/services/services-for-business/corporate-and-commercial/buying-selling-a-business"
                message2 = "We have your contact details. One of the lawyers will be in touch soon. I am now transferring you to some further information which I hope you will find useful. https://www.fjg.co.uk/services/services-for-business/corporate-and-commercial/buying-selling-a-business"
        
        
        if self.intent_name == 'contract_review_intent':
            self.sessattr['practicetype'] = practice_list[1]
            for item in personal_info:
                if self.slots[item] is not None:
                    self.sessattr[item] = self.slots[item]
                elif item not in self.sessattr:
                    self.sessattr[item] = 'to_be_filled'
                    function_name = str_to_function_name['get_'+item]
                    return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name][item])
                elif self.sessattr[item] == 'to_be_filled':
                    self.slots[item] = self.InputText
                    self.sessattr[item] = self.slots[item]
            if 'contsort' not in self.sessattr:
                self.sessattr['contsort'] = 'to_be_filled'
                return get_contsort(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name]['contsort'])
            elif self.sessattr['contsort'] == 'to_be_filled':
                self.slots['contsort'] = self.InputText
                self.sessattr['contsort'] = self.slots['contsort']
            slot_list = full_slot_list[self.intent_name]
            message1 = "Thank you, we have your contact details. If you are able to could you please email the contract to commercial@fjg.co.uk. When we have reviewed the contract we will then be in touch to discuss your requirements and we will be able to let you have a quote for the work necessary to carry out any review or amendment. You will not be committed to pay anything until after you have accepted our estimate. Thank you for contacting Fisher Jones Greenwood Solicitors."
            message2 = "We have your contact details. If you are able to could you please email the contract to commercial@fjg.co.uk. When we have reviewed the contract we will then be in touch to discuss your requirements and we will be able to let you have a quote for the work necessary to carry out any review or amendment. You will not be committed to pay anything until after you have accepted our estimate. Thank you for contacting Fisher Jones Greenwood Solicitors."
            
            
        if self.intent_name == 'draft_update_TnC_Contracts_intent':
            self.sessattr['practicetype'] = practice_list[2]
            if self.slots[slot_y_n_choices] is None and slot_y_n_choices not in self.sessattr:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1'][slot_y_n_choices]})
            if self.slots[slot_y_n_choices] is not None: 
                self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
            if self.sessattr[slot_y_n_choices].lower() == 'yes':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                slot_list = full_slot_list[self.intent_name+'_1']
                message1 = "Thank you, we have your contact details. If you are able to could you please email the terms and conditions to commercial@fjg.co.uk and we will get back to you as soon as possible. We will then be able to give you an estimate of our fees. Typically we can update a set of terms and conditions for between £300 and £600 plus VAT. You will not be committed to paying anything until you have accepted our estimate. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. If you are able to could you please email the terms and conditions to commercial@fjg.co.uk and we will get back to you as soon as possible. We will then be able to give you an estimate of our fees. Typically we can update a set of terms and conditions for between £300 and £600 plus VAT. You will not be committed to paying anything until you have accepted our estimate. Thank you for contacting Fisher Jones Greenwood Solicitors."
            elif self.sessattr[slot_y_n_choices].lower() == 'no':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                slot_list = full_slot_list[self.intent_name+'_2']
                message1 = "Thank you. We have your contact details. We will be in touch as soon as possible to talk through your requirements. We will then be able to give you an estimate of our fees. Typically we can draft a set of terms and conditions for between £300 and £600 plus VAT. You will not be committed to paying anything until you have accepted our estimate. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. We will be in touch as soon as possible to talk through your requirements. We will then be able to give you an estimate of our fees. Typically we can draft a set of terms and conditions for between £300 and £600 plus VAT. You will not be committed to paying anything until you have accepted our estimate. Thank you for contacting Fisher Jones Greenwood Solicitors."
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                
        if self.intent_name == "Employment_contracts_intent":
            self.sessattr['practicetype'] = practice_list[3]
            if self.slots[slot_y_n_choices] is None and slot_y_n_choices not in self.sessattr:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1'][slot_y_n_choices]})
            if self.slots[slot_y_n_choices] is not None: 
                self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
            if self.sessattr[slot_y_n_choices].lower() == 'yes':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr: 
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled':
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                if self.slots['nofemployees'] == None and 'nofemployees' not in self.sessattr:
                    return get_nofemployees(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1']['nofemployees'])
                else:
                    self.sessattr['nofemployees'] = self.slots['nofemployees']
                slot_list = full_slot_list[self.intent_name+'_1']
                message1 = "Thank you. We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors." 
            elif self.sessattr[slot_y_n_choices].lower() == 'no':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled':
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                if self.slots['nofemployees'] == None and 'nofemployees' not in self.sessattr:
                    return get_nofemployees(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2']['nofemployees'])
                else:
                    self.sessattr['nofemployees'] = self.slots['nofemployees']
                slot_list = full_slot_list[self.intent_name+'_2']
                message1 = "Thank you. We have your contact details. One of the lawyers will be in touch soon. You won't incur any charges until you have accepted any estimate given for work to be done. Thank you for contacting Fisher Jones Greenwood Solicitors"
                message2 = "We have your contact details. One of the lawyers will be in touch soon. You won't incur any charges until you have accepted any estimate given for work to be done. Thank you for contacting Fisher Jones Greenwood Solicitors"
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                
        if self.intent_name == "Employment_policies_and_procedures_intent":
            self.sessattr['practicetype'] = practice_list[4]
            if self.slots[slot_y_n_choices] is None and slot_y_n_choices not in self.sessattr:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1'][slot_y_n_choices]})
            if self.slots[slot_y_n_choices] is not None:
                self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
            if self.sessattr[slot_y_n_choices].lower() == 'yes':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled':
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                if self.slots['nofemployees'] == None and 'nofemployees' not in self.sessattr:
                    return get_nofemployees(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1']['nofemployees'])
                else:
                    self.sessattr['nofemployees'] = self.slots['nofemployees']
                slot_list = full_slot_list[self.intent_name+'_1']
                message1 = "Thank you. We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            elif self.sessattr[slot_y_n_choices].lower() == 'no':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled':
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                if self.slots['nofemployees'] == None and 'nofemployees' not in self.sessattr:
                    return get_nofemployees(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2']['nofemployees'])
                else:
                    self.sessattr['nofemployees'] = self.slots['nofemployees']
                slot_list = full_slot_list[self.intent_name+'_2']
                message1 = "Thank you. We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                
        if self.intent_name == "Employment_dispute_make_claim":
            self.sessattr['practicetype'] = practice_list[5]
            if self.slots[slot_y_n_choices] is None and slot_y_n_choices not in self.sessattr:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1'][slot_y_n_choices]})
            if self.slots[slot_y_n_choices] is not None:
                self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
            if self.sessattr[slot_y_n_choices].lower() == 'yes':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled':
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                slot_list = full_slot_list[self.intent_name+'_1']
                message1 = "Thank you. We have your contact details. We will be in touch soon. Legal fees can range depending on the complexity of the issues involved, the number of witnesses involved in the case and the legal arguments that require to be made. Typical unfair dismissal cases which are represented on from start to finish cost between £9000 plus VAT and disbursements and £25,000 plus VAT plus disbursements. You might be able to settle your claim in the early stages of a dispute and engaging in successful alternative dispute resolution can significantly reduce costs overall. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. We will be in touch soon. Legal fees can range depending on the complexity of the issues involved, the number of witnesses involved in the case and the legal arguments that require to be made. Typical unfair dismissal cases which are represented on from start to finish cost between £9000 plus VAT and disbursements and £25,000 plus VAT plus disbursements. You might be able to settle your claim in the early stages of a dispute and engaging in successful alternative dispute resolution can significantly reduce costs overall. Thank you for contacting Fisher Jones Greenwood Solicitors."
            elif self.sessattr[slot_y_n_choices].lower() == 'no':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2']['companyname'])
                elif self.sessattr["companyname"] == 'to_be_filled': 
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                if 'disputestage' not in self.sessattr:
                    self.sessattr['disputestage'] = 'to_be_filled'
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "disputestage", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_2']['disputestage']})          
                elif self.sessattr['disputestage'] == 'to_be_filled': 
                    self.slots['disputestage'] = self.InputText
                    self.sessattr['disputestage'] = self.slots['disputestage']
                if self.slots['havedocument'] == None:    
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "havedocument", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_2']['havedocument']})
                else:
                    self.sessattr['havedocument'] = self.slots['havedocument']
                slot_list = full_slot_list[self.intent_name+'_2']
                message1 = "Thank you. We have your contact details. One of our lawyers will be in touch soon. You won't incur any charges until you have accepted any estimate given for work to be done. If you have any documents which are relevant please email them to Employment@fjg.co.uk. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. One of our lawyers will be in touch soon. You won't incur any charges until you have accepted any estimate given for work to be done. If you have any documents which are relevant please email them to Employment@fjg.co.uk. Thank you for contacting Fisher Jones Greenwood Solicitors."
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                
        if self.intent_name == "Employment_dispute_receive_claim":
            self.sessattr['practicetype'] = practice_list[6]
            if self.slots[slot_y_n_choices] is None and slot_y_n_choices not in self.sessattr:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1'][slot_y_n_choices]})
            if self.slots[slot_y_n_choices] is not None:
                self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
            if self.sessattr[slot_y_n_choices].lower() == 'yes':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled':
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                slot_list = full_slot_list[self.intent_name+'_1']
                message1 = "Thank you. We have your contact details. We will be in touch soon. Legal fees can range depending on the complexity of the issues involved, the number of witnesses involved in the case and the legal arguments that require to be made. Typical unfair dismissal cases which are represented on from start to finish cost between £9000 plus VAT and disbursements and £25,000 plus VAT plus disbursements. You might be able to settle your claim in the early stages of a dispute and engaging in successful alternative dispute resolution can significantly reduce costs overall. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. We will be in touch soon. Legal fees can range depending on the complexity of the issues involved, the number of witnesses involved in the case and the legal arguments that require to be made. Typical unfair dismissal cases which are represented on from start to finish cost between £9000 plus VAT and disbursements and £25,000 plus VAT plus disbursements. You might be able to settle your claim in the early stages of a dispute and engaging in successful alternative dispute resolution can significantly reduce costs overall. Thank you for contacting Fisher Jones Greenwood Solicitors."
            elif self.sessattr[slot_y_n_choices].lower() == 'no':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled':
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                slot_list = full_slot_list[self.intent_name+'_2']
                message1 = "Thank you. We have your contact details. One of our lawyers will be in touch soon. You won't incur any charges until you have accepted any estimate given for work to be done. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. One of our lawyers will be in touch soon. You won't incur any charges until you have accepted any estimate given for work to be done. Thank you for contacting Fisher Jones Greenwood Solicitors."
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                
        if self.intent_name == "Employment_settlement_agreement":
            self.sessattr['practicetype'] = practice_list[7]
            if self.slots[slot_y_n_choices] is None and slot_y_n_choices not in self.sessattr:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1'][slot_y_n_choices]})
            if self.slots[slot_y_n_choices] is not None:
                self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
            if self.sessattr[slot_y_n_choices].lower() == 'yes':   
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled':
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                slot_list = full_slot_list[self.intent_name+'_1']
                message1 = "Thank you. We have your contact details. We will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. We will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            elif self.sessattr[slot_y_n_choices].lower() == 'no':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled':
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                slot_list = full_slot_list[self.intent_name+'_2']
                message1 = "Thank you. We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                
        if self.intent_name == "NDA":
            self.sessattr['practicetype'] = practice_list[8]
            if self.slots[slot_y_n_choices] is None and slot_y_n_choices not in self.sessattr:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1'][slot_y_n_choices]})
            if self.slots[slot_y_n_choices] is not None:
                self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
            if self.sessattr[slot_y_n_choices].lower() == 'yes':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled': 
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                if 'otherpartycompanyname' not in self.sessattr:
                    self.sessattr['otherpartycompanyname'] = 'to_be_filled'
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "otherpartycompanyname", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1']['otherpartycompanyname']})
                elif self.sessattr['otherpartycompanyname'] == 'to_be_filled': 
                    self.slots['otherpartycompanyname'] = self.InputText
                    self.sessattr['otherpartycompanyname'] = self.slots['otherpartycompanyname']
                if 'otherpartyfirstname' not in self.sessattr:
                    self.sessattr['otherpartyfirstname'] = 'to_be_filled'
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "otherpartyfirstname", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1']['otherpartyfirstname']})
                else:
                    self.slots['otherpartyfirstname'] = self.InputText
                    self.sessattr['otherpartyfirstname'] = self.slots['otherpartyfirstname']
                if 'otherpartylastname' not in self.sessattr:
                    self.sessattr['otherpartylastname'] = 'to_be_filled'
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "otherpartylastname", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1']['otherpartylastname']})
                else:
                    self.slots['otherpartylastname'] = self.InputText
                    self.sessattr['otherpartylastname'] = self.slots['otherpartylastname']
                if 'projectname' not in self.sessattr:
                    self.sessattr['projectname'] = 'to_be_filled'
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "projectname", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1']['projectname']})
                elif self.sessattr['projectname'] == 'to_be_filled':
                    self.slots['projectname'] = self.InputText
                    self.sessattr['projectname'] = self.slots['projectname']
                slot_list = full_slot_list[self.intent_name+'_1']
                message1 = "Thank you. We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            elif self.sessattr[slot_y_n_choices].lower() == 'no':
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                if 'companyname' not in self.sessattr:
                    self.sessattr['companyname'] = 'to_be_filled'
                    return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2']['companyname'])
                elif self.sessattr['companyname'] == 'to_be_filled':
                    self.slots['companyname'] = self.InputText
                    self.sessattr['companyname'] = self.slots['companyname']
                slot_list = full_slot_list[self.intent_name+'_2']
                message1 = "Thank you. We have your contact details. We will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. We will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                
        if self.intent_name == "SHD_incorporate_new_company":
            self.sessattr['practicetype'] = practice_list[9]
            if self.slots['shdreason'] is not None:
                self.sessattr['shdreason'] = self.slots['shdreason']
            elif 'shdreason' not in self.sessattr:
                self.sessattr['shdreason'] = 'to_be_filled'
                return get_shdreason(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name]['shdreason'], buttons_shareholders_agreement)
            elif self.sessattr['shdreason'] == 'to_be_filled':
                self.slots['shdreason'] = self.InputText
                self.sessattr['shdreason'] = self.slots['shdreason']
            for item in personal_info:
                if self.slots[item] is not None:
                    self.sessattr[item] = self.slots[item]
                elif item not in self.sessattr:
                    self.sessattr[item] = 'to_be_filled'
                    function_name = str_to_function_name['get_'+item]
                    return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name][item])
                elif self.sessattr[item] == 'to_be_filled':
                    self.slots[item] = self.InputText
                    self.sessattr[item] = self.slots[item]
            if 'companyname' not in self.sessattr:
                self.sessattr['companyname'] = 'to_be_filled'
                return get_companyname(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name]['companyname'])
            elif self.sessattr['companyname'] == 'to_be_filled':
                self.slots['companyname'] = self.InputText
                self.sessattr['companyname'] = self.slots['companyname']
            if 'agreementfocus' not in self.sessattr:
                self.sessattr['agreementfocus'] = 'to_be_filled'
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "agreementfocus", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name]['agreementfocus']})
            elif self.sessattr['agreementfocus'] == 'to_be_filled': 
                self.slots['agreementfocus'] = self.InputText
                self.sessattr['agreementfocus'] = self.slots['agreementfocus']
            slot_list = full_slot_list[self.intent_name]
            message1 = "Thank you. We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            message2 = "We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            
            
        #------------------------------------Commercial property-----------------------------------------
        if self.intent_name == "Commercial_lease_acting_for_landlord":
            self.sessattr['practicetype'] = practice_list[10]
            if self.slots['tenant_landlord'] is None and 'tenant_landlord' not in self.sessattr:
                return elicit_slot(self.sessattr, self.intent_name, self.slots, "tenant_landlord", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1']['tenant_landlord']}, commercial_tenant_landlord_button)
            if self.slots['tenant_landlord'] is not None:
                self.sessattr['tenant_landlord'] = self.slots['tenant_landlord']
            if self.slots[slot_y_n_choices] == None and slot_y_n_choices not in self.sessattr:
                if self.sessattr['tenant_landlord'].lower() == "landlord":
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1'][slot_y_n_choices+'_1']})
                else:
                    return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1'][slot_y_n_choices+'_2']})            
            if self.slots[slot_y_n_choices] is not None:
                self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
            if self.sessattr[slot_y_n_choices].lower() == 'yes':
                if self.slots['comm_private_property'] is None and 'comm_private_property' not in self.sessattr:
                    self.slots['comm_private_property'] = 'to_be_filled'
                    return elicit_slot(self.sessattr, self.intent_name, self.slots, "comm_private_property", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1']['comm_private_property']}, commercial_private_lease_button)
                elif self.slots['comm_private_property'] == 'to_be_filled':
                    self.slots['comm_private_property'] = self.InputText
                else:
                    self.sessattr['comm_private_property'] = self.slots['comm_private_property']
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                slot_list = full_slot_list[self.intent_name+'_1']
                message1 = "Thank you. We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            elif self.sessattr[slot_y_n_choices].lower() == 'no':
                if self.slots['comm_private_property'] is None and 'comm_private_property' not in self.sessattr:
                    self.slots['comm_private_property'] = 'to_be_filled'
                    return elicit_slot(self.sessattr, self.intent_name, self.slots, "comm_private_property", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_2']['comm_private_property']}, commercial_private_lease_button)
                elif self.slots['comm_private_property'] == 'to_be_filled':
                    self.slots['comm_private_property'] = self.InputText
                else:
                    self.sessattr['comm_private_property'] = self.slots['comm_private_property']
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                slot_list = full_slot_list[self.intent_name+'_2']
                message1 = "Thank you. We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                message2 = "We have your contact details. One of the lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})

        #------------------------------------Dispute Resolution-----------------------------------------
        if self.intent_name == "Personal_injury":
            self.sessattr['practicetype'] = practice_list[13]
            if self.slots[slot_y_n_choices] == None and slot_y_n_choices not in self.sessattr:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1']['injury']}) 
            if self.slots[slot_y_n_choices] is not None:
                self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
            if self.sessattr[slot_y_n_choices].lower() == 'yes':
                if self.slots["accidenttime"] is None and 'accidenttime' not in self.sessattr: 
                    return get_accidenttime(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1']['accidenttime'])
                if self.slots["accidenttime"] is not None:
                    self.sessattr['accidenttime'] = self.slots['accidenttime']
                if self.sessattr["accidenttime"].lower() == 'yes':
                    for item in personal_info:
                        if self.slots[item] is not None:
                            self.sessattr[item] = self.slots[item]
                        elif item not in self.sessattr:
                            self.sessattr[item] = 'to_be_filled'
                            function_name = str_to_function_name['get_'+item]
                            return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1'][item])
                        elif self.sessattr[item] == 'to_be_filled':
                            self.slots[item] = self.InputText
                            self.sessattr[item] = self.slots[item]
                    if 'casedesc' not in self.sessattr:
                        self.sessattr['casedesc'] = 'to_be_filled'
                        return get_casedesc(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_1']['casedesc'])
                    if self.sessattr['casedesc'] == 'to_be_filled':
                        self.slots['casedesc'] = self.InputText
                        self.sessattr['casedesc'] = self.slots['casedesc']
                    slot_list = full_slot_list[self.intent_name+'_1']
                    message1 = "Thank you. We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                    message2 = "We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors." 
                if self.sessattr["accidenttime"].lower() == 'no':
                    for item in personal_info:
                        if self.slots[item] is not None:
                            self.sessattr[item] = self.slots[item]
                        elif item not in self.sessattr:
                            self.sessattr[item] = 'to_be_filled'
                            function_name = str_to_function_name['get_'+item]
                            return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2'][item])
                        elif self.sessattr[item] == 'to_be_filled':
                            self.slots[item] = self.InputText
                            self.sessattr[item] = self.slots[item]
                    if 'casedesc' not in self.sessattr:
                        self.sessattr['casedesc'] = 'to_be_filled'
                        return get_casedesc(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2']['casedesc'])
                    if self.sessattr['casedesc'] == 'to_be_filled':
                        self.slots['casedesc'] = self.InputText
                        self.sessattr['casedesc'] = self.slots['casedesc']
                    slot_list = full_slot_list[self.intent_name+'_1']
                    message1 = "Thank you. We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                    message2 = "We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
            elif self.sessattr[slot_y_n_choices].lower() == 'no':
                if self.slots["claimagainst"] is None and 'claimagainst' not in self.sessattr:
                    return get_claimagainst(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_3']['claimagainst'])
                if self.slots["claimagainst"] is not None:
                    self.sessattr['claimagainst'] = self.slots['claimagainst']
                if self.sessattr["claimagainst"].lower() == 'yes':
                    for item in personal_info:
                        if self.slots[item] is not None:
                            self.sessattr[item] = self.slots[item]
                        elif item not in self.sessattr:
                            self.sessattr[item] = 'to_be_filled'
                            function_name = str_to_function_name['get_'+item]
                            return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_3'][item])
                        elif self.sessattr[item] == 'to_be_filled':
                            self.slots[item] = self.InputText
                            self.sessattr[item] = self.slots[item]
                    slot_list = full_slot_list[self.intent_name+'_2']
                    message1 = "Thank you. We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                    message2 = "We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                elif self.sessattr['claimagainst'].lower() == 'no':
                    for item in personal_info:
                        if self.slots[item] is not None:
                            self.sessattr[item] = self.slots[item]
                        elif item not in self.sessattr:
                            self.sessattr[item] = 'to_be_filled'
                            function_name = str_to_function_name['get_'+item]
                            return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_4'][item])
                        elif self.sessattr[item] == 'to_be_filled':
                            self.slots[item] = self.InputText
                            self.sessattr[item] = self.slots[item]
                    slot_list = full_slot_list[self.intent_name+'_2']
                    message1 = "Thank you. We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                    message2 = "We have your contact details. One of our lawyers will be in touch soon. Thank you for contacting Fisher Jones Greenwood Solicitors."
                else:
                    return get_claimagainst(self.sessattr, self.intent_name, self.slots, "Please give a valid answer to the above question.")
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                    
        #------------------------------------Wills, lasting power of attorney-----------------------------------------    
        if self.intent_name == "Wills_fact_finding_intent":
            self.sessattr['practicetype'] = practice_list[14]
            if self.slots[slot_y_n_choices] is None and slot_y_n_choices not in self.sessattr:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name+'_1'][slot_y_n_choices]})
            if self.slots[slot_y_n_choices] is not None:
                self.sessattr[slot_y_n_choices] = self.slots[slot_y_n_choices]
            if self.sessattr[slot_y_n_choices].lower() == 'yes':
                return close(self.sessattr, "Close", "Fulfilled", {"contentType": "PlainText", "content": "Please follow this link: https://fjg.wills.settify.co.uk/willslanding/d-wl-landing"})
            elif self.sessattr[slot_y_n_choices].lower() == 'no':    
                for item in personal_info:
                    if self.slots[item] is not None:
                        self.sessattr[item] = self.slots[item]
                    elif item not in self.sessattr:
                        self.sessattr[item] = 'to_be_filled'
                        function_name = str_to_function_name['get_'+item]
                        return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name+'_2'][item])
                    elif self.sessattr[item] == 'to_be_filled':
                        self.slots[item] = self.InputText
                        self.sessattr[item] = self.slots[item]
                slot_list = full_slot_list[self.intent_name+'_2']
                message1 = "Thank you for that. We have your contact details. One of our lawyers will be in touch soon."
                message2 = "We have your contact details. One of the lawyers will be in touch soon."
            else:
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, slot_y_n_choices, {"contentType": "PlainText", "content": "Please give a valid answer to the above question."})
                
        if self.intent_name == "LPA_intent":
            self.sessattr['practicetype'] = practice_list[15]
            if self.slots["attorneytype"] is None and 'attorneytype' not in self.sessattr:
                return elicit_slot(self.sessattr, self.intent_name, self.slots, "attorneytype", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name]['attorneytype']}, buttons_attorney_type)
            if self.slots["attorneytype"] is not None:
                self.sessattr['attorneytype'] = self.slots['attorneytype']
            if self.slots["singlecouple"] is None and 'singlecouple' not in self.sessattr:
                return elicit_slot(self.sessattr, self.intent_name, self.slots, "singlecouple", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name]['singlecouple']}, buttons_single_couple)
            if self.slots["singlecouple"] is not None:
                self.sessattr['singlecouple'] = self.slots['singlecouple']
            for item in personal_info:
                if self.slots[item] is not None:
                    self.sessattr[item] = self.slots[item]
                elif item not in self.sessattr:
                    self.sessattr[item] = 'to_be_filled'
                    function_name = str_to_function_name['get_'+item]
                    return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name][item])
                elif self.sessattr[item] == 'to_be_filled':
                    self.slots[item] = self.InputText
                    self.sessattr[item] = self.slots[item]
            slot_list = full_slot_list[self.intent_name]
            message1 = "Thank you for that. We have your contact details. One of our lawyers will be in touch soon."
            message2 = "We have your contact details. One of the lawyers will be in touch soon."
        
        if self.intent_name == 'Trusts_fact_finding_intent':
            self.sessattr['practicetype'] = practice_list[16]
            for item in personal_info:
                if self.slots[item] is not None:
                    self.sessattr[item] = self.slots[item]
                elif item not in self.sessattr:
                    self.sessattr[item] = 'to_be_filled'
                    function_name = str_to_function_name['get_'+item]
                    return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name][item])
                elif self.sessattr[item] == 'to_be_filled':
                    self.slots[item] = self.InputText
                    self.sessattr[item] = self.slots[item]
            slot_list = full_slot_list[self.intent_name]
            message1 = "Thank you for that. We have your contact details. One of our lawyers will be in touch soon."
            message2 = "We have your contact details. One of the lawyers will be in touch soon."
    
        if self.intent_name == 'Probate_fact_finding_intent':
            self.sessattr['practicetype'] = practice_list[17]
            for item in personal_info:
                if self.slots[item] is not None:
                    self.sessattr[item] = self.slots[item]
                elif item not in self.sessattr:
                    self.sessattr[item] = 'to_be_filled'
                    function_name = str_to_function_name['get_'+item]
                    return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name][item])
                elif self.sessattr[item] == 'to_be_filled':
                    self.slots[item] = self.InputText
                    self.sessattr[item] = self.slots[item]
            slot_list = full_slot_list[self.intent_name]
            message1 = "Thank you for that. We have your contact details. One of our lawyers will be in touch soon."
            message2 = "We have your contact details. One of the lawyers will be in touch soon."
            
        if self.intent_name == 'Equity_release_fact_finding_intent':
            self.sessattr['practicetype'] = practice_list[18]
            for item in personal_info:
                if self.slots[item] is not None:
                    self.sessattr[item] = self.slots[item]
                elif item not in self.sessattr:
                    self.sessattr[item] = 'to_be_filled'
                    function_name = str_to_function_name['get_'+item]
                    return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name][item])
                elif self.sessattr[item] == 'to_be_filled':
                    self.slots[item] = self.InputText
                    self.sessattr[item] = self.slots[item]
            slot_list = full_slot_list[self.intent_name]
            message1 = "Thank you for that. We have your contact details. One of our lawyers will be in touch soon."
            message2 = "We have your contact details. One of the lawyers will be in touch soon."
            
        #------------------------------------Immigration-----------------------------------------            
        if self.intent_name == "Immigration":
            self.sessattr['practicetype'] = practice_list[19]
            if self.slots['curr_residence'] is not None:
                self.sessattr['curr_residence'] = self.slots['curr_residence']
            elif 'curr_residence' not in self.sessattr:
                self.sessattr['curr_residence'] = 'to_be_filled'
                return elicit_slot_without_button(self.sessattr, self.intent_name, self.slots, "curr_residence", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name]['curr_residence']})
            elif self.sessattr['curr_residence'] == 'to_be_filled':
                self.slots['curr_residence'] = self.InputText
                self.sessattr['curr_residence'] = self.slots['curr_residence']
            if self.slots["type_visa"] is None and 'type_visa' not in self.sessattr:
                return elicit_slot(self.sessattr, self.intent_name, self.slots, "type_visa", {"contentType": "PlainText", "content": full_intent_slot_message[self.intent_name]['type_visa']}, buttons_type_visa)
            if self.slots['type_visa'] is not None:
                self.sessattr['type_visa'] = self.slots['type_visa']    
            for item in personal_info:
                if self.slots[item] is not None:
                    self.sessattr[item] = self.slots[item]
                elif item not in self.sessattr:
                    self.sessattr[item] = 'to_be_filled'
                    function_name = str_to_function_name['get_'+item]
                    return function_name(self.sessattr, self.intent_name, self.slots, full_intent_slot_message[self.intent_name][item])
                elif self.sessattr[item] == 'to_be_filled':
                    self.slots[item] = self.InputText
                    self.sessattr[item] = self.slots[item]
            slot_list = full_slot_list[self.intent_name]
            message1 = "Thank you for that. We have your contact details. One of our lawyers will be in touch soon in order that we can discuss this matter with you in more depth. \
                        Alternatively, you can contact the Immigration Team on 01206 835270."
            message2 = "We have your contact details. One of the lawyers will be in touch soon in order that we can discuss this matter with you in more depth. \
                        Alternatively, you can contact the Immigration Team on 01206 835270."
        
        response = save_into_table_closing_remark(intent_request, self.table, self.sessattr, self.slots, slot_list, message1, message2)
        return response

        
def lambda_handler(event, context):
    rpi = response_per_intent(event)
    slot_y_n_choices = rpi.find_slot_in_y_n_intent_slot()
    return rpi.ff_questions(slot_y_n_choices, event)



























