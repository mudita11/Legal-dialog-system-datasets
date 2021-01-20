# Legal service dialog system

Source code and linguistic resources for a legal dialog system

This repository consists of code for FAQ, FF, restart and greeting handlers.

In addition it consists of various linguistic resources including training dataset and conversation testset, especially designed for legal doamin. 

conversation_test_set.xlsx consists of conversation flows designed to test all possible unique conversations between a user and dialog system. Each conversation flow is a multi-turn conversation consisting of a number of sentences. A odd numbered tabs in the spreadsheet consists of conversations follwed by even numbered tabs with their respective intents. 

test_unseen_sent.py tests each conversation and generates a report showing number of conversations correctly identified by the system. Before testing a conversation, the session is restarted.
