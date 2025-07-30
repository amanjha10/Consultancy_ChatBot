#!/usr/bin/env python3
import requests

# Test escalation with different queries
queries = [
    'xyzabc123 nonsensical query',
    'I need urgent help that the bot cannot handle',
    'This is a very complex legal issue requiring human expert assistance',
    'Help me with something the automated system cannot understand'
]

print('Testing escalation triggers...')

for i, query in enumerate(queries, 1):
    print(f'\nTest {i}: {query[:50]}...')
    response = requests.post('http://localhost:5000/chat', json={'message': query})
    
    if response.status_code == 200:
        data = response.json()
        print(f'  Escalated: {data.get("escalated", False)}')
        print(f'  Type: {data.get("type", "Unknown")}')
        print(f'  Response length: {len(data.get("response", ""))}')
        print(f'  Response preview: {data.get("response", "")[:100]}...')
    else:
        print(f'  Failed: {response.status_code}')
