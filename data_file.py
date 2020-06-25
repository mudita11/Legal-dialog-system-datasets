utt_map_intent = {"amend_will":"faq_amend_will_intent","appl_check_visa":"faq_appl_check_visa_intent", "appl_check_visa":"faq_appl_check_visa_intent", "appl_claim_length":"faq_application_claim_length_intent", "appointment_diff_office":"faq_appointment_diff_office_intent", "appointment_length":"faq_appointment_length_intent", "arrange_witness_test_utt":"faq_arrange_witness_intent", "attend_meeting_someone":"faq_attend_meeting_sone_intent", "boundary_neighbor_dispute":"faq_boundary_neighbor_dispute_intent", "CCJ":"faq_CCJ_intent", "copy_will":"faq_copy_will_intent", "cost_test_utt":"faq_cost_legalaid_intent", "court_hearing_visa":"faq_court_hearing_visa_intent", "director_not_acting_properly":"faq_director_not_acting_properly_intent", "disparaging_statement":"faq_disparaging_statement_intent", "employment_tribunal":"faq_employment_tribunal_intent", "expired_visa":"faq_expired_visa_intent", "home_visit":"faq_home_visit_intent", "interpreter_visa":"faq_interpreter_visa_intent", "legal_aid":"faq_legal_aid_intent", "no_win_no_fee":"faq_no_win_no_fee_intent", "old_claim":"faq_old_claim_intent", "PI_MN":"faq_PI_MN_intent", "prepare_appointment":"faq_prepare_appointment_intent", "refusal_letter_visa":"faq_refusal_letter_visa_intent", "settlement_agreement":"faq_settlement_agreement_intent", "store_will":"faq_store_will_intent", "user_owed_money_company":"faq_user_owed_money_company_intent", "user_owed_money":"faq_user_owed_money_intent", "validity_will":"faq_validity_will_intent", "faq_open_time":"general_faq_open_time",
    "biz_sales_and_purchase":"get_details", "contract_review":"contract_review_intent", "draft_update_TnC":"draft_update_TnC_Contracts_intent", "greet_test_utt": "greet_intent",
    "info_test_utt": "user_choice_to_general_info_intent", "touch_test_utt": "user_choice_to_contact_solicitor_intent",
    "session_restart": "restart_session_intent",
    "slot_yes_no":"not-an-intent-yes-no", "slot_button_practicetype":"not-an-intent-practicetype"}

main_test_utt = {
################################## Single-turn ###################################
"amend_will": ["what happens to my old will", "what is the process to change my will", "how do i make amendments to my will", "can i change my will", "how often should i change my will"], \
"appl_check_visa": ["do you provide application checking service"], \
"appl_claim_length": ["how long will my application take", "how does the process work", "what should i expect", "can this be done in one appointment", "how long does the process take", "how long will my claim take"], \
"appointment_diff_office": ["i am not resident at Colchester can I visit one of your other offices for an appointment", "i would like to see someone in Chelmsford as i cannot travel", "i would like to see someone in Billericay as i cannot travel", "i would like to see someone in Holland on Sea as i cannot travel", "i would like to see someone in Colchester as i cannot travel", "i would like to see someone in Clacton as i cannot travel"], \
"appointment_length": ["how long would this appointment last", "does the appointment take a long time"], \
"arrange_witness_test_utt" : ["can a beneficiary witness my will", "i do not have anyone available to witness my will can you help", "do you provide witness for my will"], \
"attend_meeting_someone": ["can i bring a friend in with me to the appointment", "do i have to attend the meeting with my civil partner", "do i have to attend the meeting with my spouse", "do i have to attend the meeting with my partner", "the person that i need advice on lives in another country so will i be able to find out all i need without him her being with me at the initial appointment", "do you help people who wish to obtain visas for other countries", "can i bring along my partner or somebody else to the appointment", "do i have to be on my own in the appointment", "is someone else able to be in the appointment with me", "do i need to bring anyone with me", "can i come to the meeting on my own"], \
#incomplete
"boundary_neighbor_dispute": ["i am a minority shareholder in a business and i have a dispute with the other shareholders what can i do", "i am a majority shareholder in a business and i have a dispute with the other shareholders can you help", "i am in dispute with my other directors in my business can you help", "can you help with a dispute with my other shareholders", "can you help with a dispute with my other directors", "i am in deadlock with my other shareholder what can i do", "i have a share in a company and we can not agree on the way forward what can i do", "i have a dispute with a shareholder what can I do", "i have a dispute with my fellow directors what can I do", "what happens if directors and shareholders of a company disagree on something", "i have a dispute with my neighbor can you help me", "i need help with a building dispute", "can you help with a building dispute", "the builders i employed have been guilty of defective work and i need help", "do you deal with building disputes", "i am in dispute with a builder about a job he did can you help", "i am involved in a construction dispute a contractor carried out work on my house and it is not upto standard can you help", "a builder has messed up a contract what can i do", "i am in dispute with my neighbour about some land", "my next door neighbour has taken some of my land", "i need assistance with a boundary dispute", "what can i do about my neighbour who has taken part of my land", "my neighbour has fenced off part of my garden", "my neighbour has taken part of my land and put a fence around it", "how do i find out if my neighbour has come across my boundary", "i need help with a boundary dispute", "my neighbor has encroached on my land what can i do", "i have a boundary dispute with a neighbor what can I do to address this"], \
"CCJ": ["i have a county court judgement against me and it has affected my credit rating what can i do", "can i get a judgement entered against me removed", "what can i do if someone enters a judgement against me", "can you help me with a judgement entered against me", "i have received a judgement and do not know what to do", "someone has entered judgement against me and i do not know what to do", "i have a county court judgement gainst me what do i do to have it removed"], \
"copy_will": ["do i need a copy of my will"], \
#incomplete
"cost_test_utt": ["Will there be any additional fees to your fee?", "what are the costs to your services if i am not entitled to legal aid?", "Is it free to amend a visa?", "How much do you charge for ​will amendments?", "how much do you charge to prepare a ​will?", "what are the costs for your services if i am not entitled to legal aid?", "what is the cost of making a ​will​ if i am not entitled to legal aid?", "do you deal with ​willa? How much do you charge?", "i need a cost estimate for legal proceedings.", "how much will it cost for you to act for me on a wildcard dispute?", "I have a dispute but need to know how much it will cost me before i instruct?", "How much will legal proceedings cost overall?"], \
"court_hearing_visa": ["i have a court hearing if i instruct you will you attend"], \
"director_not_acting_properly": ["what happens if a director acts improperly", "i think one of the directors in my business has acted improperly. what are my options", "my fellow directors are not acting properly can you help", "i think that a director of a company of which i am a shareholder is not acting properly. whatshould i do"], \
"disparaging_statement": ["i need help with a defamation claim", "i need help with a claim for slander", "i need help with a claim for libel", "can you help me with a claim for slander", "can you help me with a claim for libel", "can you help with defamation", "someone has published lies about me what can i do", "someone is lying about me what can i do", "how do i claim damages for slander", "how do i claim damages for libel", "my employer has made untrue remarks about me", "my employee is lying about me to other people", "someone has posted lies about me on instagram", "someone has posted lies about me on twitter", "someone has posted lies about me on facebook", "someone has posted lies about me on social media", "someone has written lies about me", "i have been slandered and want to do something about it", "someone has said something disparaging about me which is untrue what can I do to addressthis"], \
"employment_tribunal": ["i need someone to act for me on an employment claim", "do you represent people in employment tribunals", "i want someone to act for me in an employment tribunal claim", "i need representation in an employment tribunal claim", "i am claiming against my employer can you help", "do you deal with employment claims", "i need help with an employment claim", "i am in dispute with my employer who has sacked me can you help", "i need advice on making a claim against my employer", "can you help with an employment claim", "i want to claim against my employer can you help", "i want to take my employer to an employment tribunal can you help"], \
"expired_visa": ["my visa has expired can you still help me"], \
#incomplete
"home_visit": ["do you offer home visits and if so how much do you charge?", "i can not get into the office for an appointment do you offer telephone appointments", "do you provide home appointments", "i want to know if home appointments are available", "will i have to attend your office on numerous occasions", "i am not resident at colchester can i visit one of your other offices or an appointment", "can i have a telephone appointment or do i need to attend the office", "is it more expensive for you to come to my home", "do i have to come to the office"], \
"interpreter_visa": ["are interpretors provided?"], \
#inclomplete
"legal_aid": ["which locations you cover under legal aid i do not live in essex", "do you offer legal aid", "do you give free legal advice"], \
"no_win_no_fee": ["how much of my damages do you take for your costs under a no win no fee arrangement", "do you offer no win no fee arrangement"], \
"old_claim": ["the negligence that i want to bring a claim for happened a long time ago can i still bring a claim"], \
"PI_MN": ["do i have a good claim for medical negligence", "do i have a good claim for personal injury", "i have been injured in a car accident do you take on these kind of cases", "i have been injured in a public place do you take on these kind of cases", "i have been injured at work do you take on these kind of cases"], \
#inclomplete
"prepare_appointment": ["what do i need to bring to the appointment", "what do i need to bring with me at the appointment", "do i need to bring id with me", "do i need to prepare anything for my appointment"], \
"refusal_letter_visa": ["i have had a refusal letter from the home office is this something you can assist with"], \
"settlement_agreement": ["i need advice on a settlement agreement do you offer this service", "do you have solicitors who deal with settlement agreements", "i need to see someone about a settlement agreement", "i need a solicitor for a settlement agreement", "do you deal with settlement agreements", "my employer wants to offer me a settlement agreement can you help with that", "my employer has offered me a settlement agreement can you help me with this"], \
"store_will": ["where do i store my will"], \
#incomplete
"user_owed_money_company": ["how do i claim against an insolvent company", "how do i claim against an insolvent business", "a business i supply is being wound up what are my options for recovering the money", "what chance have i got of recovering money from an insolvent company", "one of my debtors has stopped trading what can i do", "what can i do if a debtor is insolvent", "i am worried that my customer is going bust what can i do", "i am afraid that a company that owes me money is about to become insolvent what should i do"], \
"user_owed_money": ["my customer has outstanding debts to me and i want to recover them", "i have been waiting for payment for a debt but it still has not been paid what can i do", "someone has not paid me for work i have done what can i do", "i need help to get money owed to me", "i want help to get my money from a debtor", "i need help to recover a debt", "i want help with a debt", "can you help recover outstanding debts", "how do i issue proceedings to recover a debt", "my customer is refusing to pay my bills what is the best thing to do", "i am owed money by a customer what can i do", "my customer has not paid my bill what is the best thing to do", "i have lent some money to my sister and they would not pay it back what can i do", "i have lent some money to my brother and they would not pay it back what can i do", "i have lent some money to my family and they would not pay it back what can i do", "i have lent some money to my friend and they would not pay it back what can i do", "i am owed money by someone what can I do to recover it"], \
"validity_will": ["how long does a will last"], \
"faq_open_time": ["i need to pop in with my id are you open on a saturday as i am at work all week", "can i come to the office at the weekend", "can i come to the office in the evenings", "what time do you close", "what time do you open", "are you open on a sunday", "do you open at the weekend", "what are your opening hours"], \
"biz_sales_and_purchase": ["I am buying an anything business. Can you help me?"], \
"contract_review": ["can you help me with contract review?"], \
"draft_update_TnC": ["can you draft me a contract?", "can you help me with my TnC?", "can you help me with my terms and conditions?", "i want to update my TnCs", "i want to update my terms and conditions", "i need my terms and conditions updating", "i need some new terms and conditions.", "can you draft me some terms and conditions?"], \
#"employment" : [], \
"NDA" : [], \
"shareholders_agreement" : [], \
"commercial_lease_landlord" : [], \
"commercial_lease_tenant" : [], \
"sell_comm_property" : [], \
"buy_comm_property" : [], \
"personal_injury" : [], \
################################## Multi-turn ####################################
"greet_test_utt" : ["hello there!"], \
#, "hey bot", "hi", "hello", "hey", "hiya", "hi there", "good morning", "good evening", "good afternoon", "morning"],
"touch_test_utt" : ["I want to get in touch with a solicitor."], \
"info_test_utt" : ["i want to ask some general questions"], \
"slot_button_practicetype": ["i want help with selling my company", "i want someone to review a contract", "can you draft me some terms and conditions", "i want someone to help me with employment contracts", "i want help with employment policies and procedures", "i want to make a claim for employment dispute", "i have received a claim for employment dispute", "i have a settlement agreement for employment dispute", "i want to make a confidentiality agreement", "i want advise on shareholding agreement to incorporate a new company", "i want advise on shareholding agreement to relate it to a specific transaction", "i want advise on shareholding agreement to relate it to a joint venture", "i want advise on shareholding agreement to relate it to a management buyout transaction", "i want to lease my premises", "i am leasing an office and need some help", "i need a lawyer to help selling my property", "i need someone to act for me on the purchase of a business property", "i need help with injury I got in a car accident"], \
################################ Restart/Resume ##################################
"session_restart" : [ "Restart the session", "restart session", "i would like to restart the session", "can i start the session again?", "start over", "can i restart the session", "i want to start over"], \
"slot_yes_no": ["yes", "no"]
}
