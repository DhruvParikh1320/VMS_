import requests
from requests.auth import HTTPBasicAuth
import json
from django.contrib import messages
def whatsapps_send_notifications(request, employee_mobile, employee_name, visitor_name, accept_url, reject_url):
    try:
        url = "https://us-central1-pristine-nomad-264707.cloudfunctions.net/SendTemplateWhatsappV2"
        
        payload = {
            "FromMobileNo": "918141540404",
            "FBToken": "EAAPcZCxtB3boBO5ANPAIGM8zOU5bJrTAZBb2BM5hZAzfZCgCo9tgPLZCwzaa6U6IAZBK8EU0f9rhdsChgoI6Fqr6vhH4INDFKu6ZCbbnSqVgZCZCFA93luOtUUyDj36YUJAcllHbNSatGlB4YI5CtqbhejCbR6L4WKxaZAkK4Glj8l5wsoGmuaWbQO9NfSfNh1nLc3f3K29Lg6yZCWC",
            "toMobileNo": employee_mobile,
            "TemplateName": "indian_infotech_visitor_confirmation",
            "TemplateLanguage": "en",
            "TemplateMsgString": f"Hello {employee_name}, your visitor {visitor_name} has arrived at the gate. Please take action:\n\n"
                                  f"To approve the visit, click {accept_url}\n"
                                  f"To reject the visit, click {reject_url}.\n\n"
                                  "Thank you for your prompt response.",
            
            "Variables": [
                {"Variable": employee_name},
                {"Variable": visitor_name},
                {"Variable": accept_url},
                {"Variable": reject_url}
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            # response_data = response.json()  # Parse the JSON response
            # messages.success(
            #         request, 
            #         f"Appointment message successfully sent.\nResponse: {response_data}\n"
            #         f"Employee: {employee_name}, Visitor: {visitor_name}\n"
            #         f"Accept URL: {accept_url}\nReject URL: {reject_url}\n"
            #         f"Mobile: {employee_mobile}", 
            #         extra_tags="success"
            #     )
            # messages.success(request, "Appointment message successfully sent.", extra_tags="success")
            response_data = response.json()  # Parse the JSON response
            
            # Check if `status` key exists and its value is 1
            if response_data.get('status') == 1:
                # messages.success(
                #     request, 
                #     f"Appointment message successfully sent.\nResponse: {response_data}\n"
                #     f"Employee: {employee_name}, Visitor: {visitor_name}\n"
                #     f"Accept URL: {accept_url}\nReject URL: {reject_url}\n"
                #     f"Mobile: {employee_mobile}", 
                #     extra_tags="success"
                # )
                messages.success(request, "Appointment message successfully sent.", extra_tags="success")
            else:
                # messages.error(
                #     request, 
                #     f"Appointment message failed. Response: {response_data}.\nResponse: {response_data}\n"
                #     f"Employee: {employee_name}, Visitor: {visitor_name}\n"
                #     f"Accept URL: {accept_url}\nReject URL: {reject_url}\n"
                #     f"Mobile: {employee_mobile}", 
                #     extra_tags="success"
                # )
                messages.error(
                    request, 
                    f"Appointment message failed. Response: {response_data}", 
                    extra_tags="danger"
                )
        else:
            messages.error(request, "Appointment message not sent.", extra_tags="danger")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        messages.error(request, f"Error_101: {e}", extra_tags="danger")