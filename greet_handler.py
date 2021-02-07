import logging
import boto3
from fact_finding_data_store import buttons_practype_initial_options
from fix_definitions import get_slots, get_sessattr, get_userid, get_inputtranscript, close, elicit_intent, elicit_intent_without_button

client = boto3.client('lex-runtime', region_name="eu-west-1")

logger = logging.getLogger()
  
response_greet = "Hello, I can help you with the following services today. Please select from these."
response_greet_how_are_you = "Hello, I am fine thanks. I can help you with the following services today. Please select from these."
response_inform_bot_services = "I can help you with the following services today. Please select from these."
response_ask_bot_name = "You can call me legal assistant. I can help you with the following services today. Please select from these."
response_goodbye = "Take care, bye"
response_thank = "No problem. Can I help you with anything else today?"

class BasicResponseHandler:
    '''Handle basic intents.
    
    Basic intents are: 'greet_intent', 'greet_how_are_you_intent',
     'inform_bot_services_intent', 'ask_bot_name_intent',
     'goodbye_intent' and 'thank_intent.'''
    def __init__(self, intent_request):
        '''Construct all the necessary attributes for the BasicResponseHandler object.'''
        self.intent_name = intent_request['currentIntent']['name']
        self.sessattr = get_sessattr(intent_request)
        if self.sessattr is None:
            self.sessattr = dict()
            
    def intent_name_responses(self):
        '''Return json output for the six basic intents.'''
        if self.intent_name == 'greet_intent':
            return elicit_intent(
                        self.sessattr,
                        {"contentType":"PlainText",
                         "content": response_greet},
                         buttons_practype_initial_options
            )
    
        if self.intent_name == 'greet_how_are_you_intent':
            return elicit_intent(
                        self.sessattr,
                        {"contentType":"PlainText",
                         "content": response_greet_how_are_you},
                          buttons_practype_initial_options
            )
        
        if self.intent_name == 'inform_bot_services_intent':
            return elicit_intent(
                        self.sessattr,
                        {"contentType":"PlainText",
                        "content": response_inform_bot_services},
                        buttons_practype_initial_options
            )
    
        if self.intent_name == 'ask_bot_name_intent':
            return elicit_intent(
                        self.sessattr, {
                        "contentType":"PlainText",
                        "content": response_ask_bot_name},
                        buttons_practype_initial_options
            )
        
        if self.intent_name == 'goodbye_intent':
            return close(
                    self.sessattr,
                    "Close",
                    "Fulfilled",
                    {"contentType": "PlainText",
                     "content": response_goodbye}
            )
            
        if self.intent_name == 'thank_intent':
            return close(
                    self.sessattr,
                    "Close", "Fulfilled",
                    {"contentType": "PlainText",
                     "content": response_thank}
            )
    
            
def lambda_handler(event, context):
    '''
    Create BasicResponseHandler objects and calls class methods.
    
        Arguments:
        intent_request: contains request data from lex in JSON format.
    '''
    rpi = BasicResponseHandler(event)
    return rpi.intent_name_responses()
    
