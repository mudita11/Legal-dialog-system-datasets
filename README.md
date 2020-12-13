# Regression testing on dialog system

Testing a dialog system is core to test the proper functioning of a system. This repository consists of seen_data.xlsx and test_seen_sent.py

seen_data.xlsx consists of 158 conversation flows designed to test all possible unique conversations between a user and dialog system. Each conversation flow is a multi-turn conversation consisting of few sentences. A odd numbered tabs in the spreadsheet consists of conversations follwed by even numbered tabs with correct intent for each sentence in the conversation flow. 

test_seen_sent.py tests each conversation and generates a report showing number of conversations correctly identified by the system. Correct identification is correct intent identification by the system. Before testing a conversation, the session is restarted.
