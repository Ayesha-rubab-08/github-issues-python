\# Week 7: Prompt Injection Tests



`injection-tests.json` holds 4 repeatable prompt injection test cases for the

n8n support agent (see `week6-ai-agent`).



Each test has:

\- `id`: short name of the test

\- `attack`: what the attack tries to do

\- `message`: the exact message sent to the agent

\- `expected\_tool\_used`: the tool the agent should report

\- `must\_contain`: text that must appear in the answer

\- `must\_not\_contain`: text that must NOT appear in the answer (compare in lowercase)



\## Tests

1\. `refund-false-90-days`: tries to make the agent state a false refund policy

2\. `ignore-old-instructions`: tries to make the agent ignore its rules

3\. `reveal-system-message`: tries to make the agent print its instructions

4\. `change-role`: tries to turn the agent into "DAN"



\## How to run (manual for now)

1\. Open the agent workflow in n8n and click Open chat.

2\. Send the `message` of one test.

3\. Compare the agent output with the test's expected values.



The Gemini free tier allows about 20 requests per day, so run these only when

the prompt or the model changes.

