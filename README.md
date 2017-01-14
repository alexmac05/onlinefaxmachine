# onlinefaxmachine
This application uses the HelloFax API to send a receive faxes


Steps to get up and running
1. clone repository and do setup of virtualenv
2. python faxit.py runserver
3. http://127.0.0.1:8000/
4. Start ngrok
5. ./ngrok http 8000
6. Follow the instructions here: https://faq.hellosign.com/hc/en-us/articles/216809878-Complete-Walkthrough-for-Setting-Up-The-HelloFax-API to update the callback with the new ngrok callback address
7 . Verify that the callback handler is updated https://www.hellofax.com/account/apiInfo
8. Send a fax following the instructions. Wait 5 mins and the callback will complete in that time.

