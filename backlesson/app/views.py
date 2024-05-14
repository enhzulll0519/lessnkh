from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse, HttpResponse
import json
from backlesson.settings import *
from django.views.decorators.csrf import csrf_exempt
import pytesseract
from PIL import Image
from rest_framework.decorators import api_view
import base64
import io




def extract_text_from_image(request):
    if request.method == 'POST' and request.FILES['image']:
        # Get the uploaded image
        uploaded_image = request.FILES['image']

        # Open the image using Pillow
        image = Image.open(uploaded_image)

        # Use pytesseract to extract text from the image
        extracted_text = pytesseract.image_to_string(image)

        return JsonResponse({"extracted_text": extracted_text})

    return render(request, "extract_text.html")



@api_view(['POST', 'GET'])
def b64Text(request):
    action = 'base64ToText'
    jsons = json.loads(request.body)
    action = jsons.get('action', 'nokey')
    b64 = jsons.get('base64', 'nokey')
    image_data = base64.b64decode(b64)
    image = Image.open(io.BytesIO(image_data))
    extracted_text = pytesseract.image_to_string(image)
    data = [{"text":extracted_text}]
    print(data)
    resp= sendResponse(request, 200, data, action)
    return HttpResponse(resp)
# @api_view(['POST', 'GET'])
# def b64Text(request):
#     action = 'base64ToText'
    
#     if request.method == 'POST':
#         try:
#             jsons = json.loads(request.body)
#             action = jsons.get('action', 'nokey')
#             b64 = jsons.get('base64', 'nokey')
            
#             if b64 == 'nokey':
#                 return HttpResponse(json.dumps({"error": "base64 key missing"}), content_type="application/json", status=400)

#             try:
#                 image_data = base64.b64decode(b64)
#             except (base64.binascii.Error, ValueError) as decode_error:
#                 return HttpResponse(json.dumps({"error": "Invalid base64 data"}), content_type="application/json", status=400)

#             image = Image.open(io.BytesIO(image_data))
#             extracted_text = pytesseract.image_to_string(image)
#             data = [{"text": extracted_text}]
#             print(data)
            
#             # Assuming sendResponse is a function you have defined elsewhere
#             # If sendResponse returns a JSON string, you can directly return it
#             resp = sendResponse(request, 200, data, action)
#             return HttpResponse(resp, content_type="application/json")

#         except json.JSONDecodeError:
#             return HttpResponse(json.dumps({"error": "Invalid JSON format"}), content_type="application/json", status=400)
#         except Exception as e:
#             # Log the error
#             print(f"Unhandled exception: {e}")
#             return HttpResponse(json.dumps({"error": "Internal server error"}), content_type="application/json", status=500)
    
#     return HttpResponse(json.dumps({"error": "Invalid request method"}), content_type="application/json", status=405)


def gettime(request):
    jsons = json.loads(request.body)
    action = jsons['action']

    today = datetime.now()
    data = [{'datetime':today}]
    resp = sendResponse(request, 200, data, action)
    return resp
# gettime

def dt_register(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    firstname = jsons['firstname']
    lastname = jsons['lastname']
    email = jsons['email']
    passw = jsons['passw']

    myCon = connectDB()
    cursor = myCon.cursor()
    
    query = F"""SELECT COUNT(*) AS usercount FROM t_user 
            WHERE email = '{email}' AND enabled = 1"""
    
    cursor.execute(query)
    columns = cursor.description
    respRow = [{columns[index][0]:column for index, 
        column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()

    if respRow[0]['usercount'] == 1:
        data = [{'email':email}]
        resp = sendResponse(request, 1000, data, action)
    else:
        token = generateStr(12)
        query = F"""INSERT INTO public.t_user(
	email, lastname, firstname, passw, regdate, enabled, token, tokendate)
	VALUES ('{email}', '{lastname}', '{firstname}', '{passw}'
    , NOW(), 0, '{token}', NOW() + interval \'1 day\');"""
        cursor1 = myCon.cursor()
        cursor1.execute(query)
        myCon.commit()
        cursor1.close()
        data = [{'email':email, 'firstname':firstname, 'lastname': lastname}]
        resp = sendResponse(request, 1001, data, action)
        

        sendMail(email, "Verify your email", F"""
                <html>
                <body>
                    <p>Ta amjilttai burtguulle. Doorh link deer darj burtgelee batalgaajuulna uu. Hervee ta manai sited burtguuleegui bol ene mailiig ustgana uu.</p>
                    <p> <a href="http://127.0.0.1:8000/check/?token={token}">Batalgaajuulalt</a> </p>
                </body>
                </html>
                """)

    return resp
# dt_register

def dt_login(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    email = jsons['email']
    passw = jsons['passw']
    for item in jsons['prods']:
        item['prodname']


    myCon = connectDB()
    cursor = myCon.cursor()
    
    query = F"""SELECT COUNT(*) AS usercount FROM t_user 
            WHERE email = '{email}' AND enabled = 1 AND passw = '{passw}'"""
    
    cursor.execute(query)
    columns = cursor.description
    respRow = [{columns[index][0]:column for index, 
        column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()

    if respRow[0]['usercount'] == 1:
        myCon = connectDB()
        cursor1 = myCon.cursor()
        
        query = F"""SELECT email, firstname, lastname
                FROM t_user 
                WHERE email = '{email}' AND enabled = 1 AND passw = '{passw}'"""
        
        cursor1.execute(query)
        columns = cursor1.description
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor1.fetchall()]
        cursor1.close()
        
        email = respRow[0]['email']
        firstname = respRow[0]['firstname']
        lastname = respRow[0]['lastname']

        data = [{'email':email, 'firstname':firstname, 'lastname':lastname}]
        resp = sendResponse(request, 1002, data, action)
    else:
        data = [{'email':email}]
        resp = sendResponse(request, 1004, data, action)

    return resp
#dt_login

@csrf_exempt
def checkService(request):
    if request.method == "POST":
        try :
            jsons = json.loads(request.body)
        except json.JSONDecodeError:
            

            result = sendResponse(request, 3003, [], "no action")
            return JsonResponse(json.loads(result))
        action = jsons['action']

        if action == 'gettime':
            result = gettime(request)
            return JsonResponse(json.loads(result))
        elif action == 'register':
            result = dt_register(request)
            return JsonResponse(json.loads(result))
        elif action == 'login':
            result = dt_login(request)
            return JsonResponse(json.loads(result))
        else:
            result = sendResponse(request, 3001, [], action)
            return JsonResponse(json.loads(result))
    else:
        result = sendResponse(request, 3002, [], "no action")
        return JsonResponse(json.loads(result))
#checkService

@csrf_exempt
def checkToken(request):
    token = request.GET.get('token')
    myCon = connectDB()
    cursor = myCon.cursor()
    
    query = F"""SELECT COUNT(*) AS usertokencount, MIN(email) as email, MAX(firstname) as firstname, 
                    MIN(lastname) AS lastname 
            FROM t_user 
            WHERE token = '{token}' AND enabled = 0 AND NOW() <= tokendate """
    
    cursor.execute(query)
    columns = cursor.description
    respRow = [{columns[index][0]:column for index, 
        column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()

    if respRow[0]['usertokencount'] == 1:
        query = F"""UPDATE t_user SET enabled = 1 WHERE token = '{token}'"""
        cursor1 = myCon.cursor()
        cursor1.execute(query)
        myCon.commit()
        cursor1.close()

        tokenExpired = generateStr(30)
        email = respRow[0]['email']
        firstname = respRow[0]['firstname']
        lastname = respRow[0]['lastname']
        query = F"""UPDATE t_user SET token = '{tokenExpired}', tokendate = NOW() WHERE email = '{email}'"""
        cursor1 = myCon.cursor()
        cursor1.execute(query)
        myCon.commit()
        cursor1.close()
        
        data = [{'email':email, 'firstname':firstname, 'lastname':lastname}]
        resp = sendResponse(request, 1003, data, "verified")
        sendMail(email, "Tanii mail batalgaajlaa",  F"""
                <html>
                <body>
                    <p>Tanii mail batalgaajlaa. </p>
                </body>
                </html>
                """)
    else:
        
        data = []
        resp = sendResponse(request, 3004, data, "not verified")
    return JsonResponse(json.loads(resp))
#checkToken
