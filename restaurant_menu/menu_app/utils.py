import json
import re
import pdfplumber
import base64
from io import BytesIO
from openai import OpenAI
from django.conf import settings
# import response
# import pytesseract
# import cv2
# import numpy as np


# NO PARSE; JUST UPLOAD IMG TO GBT
class PdfParse:
    def __init__(self, file, menuDescription):
        self.pdf = file
        self.menuDescription = menuDescription
        
        # Global error messages to be used for logs
        self.errorMessages = {
            'pages': [],
            'file_wide': [],
        }
        # Denotes a page wide error
        self.errorMsg = False
        self.key = settings.API_KEY
        
    def toImg(self):
        returnJson = {"description": self.menuDescription,
                "sections": []
            }
        responses = []
        try:
            with pdfplumber.open(self.pdf) as pdf:
                for i, page in enumerate(pdf.pages):
                    self.errorMsg = False
                    pilImage = page.to_image(resolution=300).original #In PIL format; need base64

                    buffer = BytesIO()
                    pilImage.save(buffer, format="PNG")
                    buffer.seek(0)

                    binImage = buffer.read()
                    b64Image = base64.b64encode(binImage).decode("utf-8")
                    print(f"Binary image created for page {i + 1}")

                    response = self.genResponse(b64Image, i+1)
                    if not self.errorMsg:
                        responses.append((True, response))
                    else: #If an error message was created for this page, stop operating for the page.
                        print(f"Response from OpenAI: page error")
                        break
                    print(f"Response from OpenAI: {response}")
                
                for page, response in enumerate(responses):
                    if isinstance(response[1][0], dict): #OpenAI provided a valid json object
                        page_data = response[1]

                    print(f"Page_data: \n{page_data}")
                    returnJson['sections'].extend(page_data) #Appending list of JSON objects to sections, a field whose value is a list.
                return (True, returnJson, self.errorMessages)

        except Exception as e:
            self.errorMessages['file_wide'].append({'error_message': f'Unexpected error occured while converting PDF to image: {e}'})
            print(f"Error converting to image: {e}")
            return (False, "", self.errorMessages)


    def genResponse(self, img, page):
        try:
            client = OpenAI(api_key=self.key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": 
                                """You are analyzing a menu that I need to turn into structured data. Provide a JSON object with these fields: 'section_name', 'menu_item', 'price', 'dietary_restriction', and 'description'. 
                                If you can't determine a field ensure its a valid JSON placeholden like 'null', except for sections. 
                                If you can't figure out a section name simply write down its section number (in the order that you reach it), but try and be more liberal when it comes to naming sections and infer only when you're confident. 
                                Most importantly, I need the relationships to be accurate, so even if you can't find the section name of something ensure the relationships are correct, for example, still make sure that the correct menu_items are children of that unamed section. 
                                You can assume a section based off of the menu_items it contains, as long as you DONT REPEAT SECTION NAMES. Also try and be a little more liberal for dietary restrictions, if its clear that a menu_item only has veggies for example then you can denote it as such, just make sure to use actual dietary restriction names (gluten-free, vegan, vegetarian, peanut-free, etc.). 
                                It also seems that you tend to interpret calories (cal.) as price, prices are always standalone digits or are preceded/followed by a currency symbol. ONLY RETURN VALID JSON, and always just return an array of JSON objects starting with section_name. 
                                This is a sample of an expected output, note that I will be appending the output to the "sections" field, I just want an array of json objects denoting each section and its respective menu_items: 
                                [
                                    {
                                    "section_name": <section_name>, 
                                    "menu_items": [ {
                                        "menu_item": "Cheesy Double Decker Taco", 
                                        "price": null, 
                                        "dietary_restriction": null, 
                                        "description": null}, ...].
                                    }, ...
                                ]     
                                Lastly, and this is very important, if you determine that the image is not a menu (or you simply are unable to parse any of it), ONLY return False as your first choice, not in JSON format. This is very important.""",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img}"
                                },
                            },
                        ],
                    }
                ],
            )
            choice = response.choices[0]
            if isinstance(choice, bool):
                self.errorMessages['pages'].append({'page': page, 'error_message': 'Failed to parse JSON content. It most likley did not have any menu content.'})
                self.errorMsg = True
                print(f"Failed to parse JSON content: {page}")
                return  
            elif hasattr(choice, 'message') and choice.message:
                content = choice.message.content
                json_match = re.search(r"```json\n(.*?)```", content, re.DOTALL)

                if json_match:
                    json_content = json_match.group(1)  # Extract the JSON part
                    json_content = json_content.strip() #Get rid of extra whitespace
                    # print(f"json_content: {json_content}")
                    try:
                        parsed_content = json.loads(json_content)  # Parse the JSON content
                        return parsed_content
                    except json.JSONDecodeError:
                        self.errorMessages['pages'].append({'page': page, 'error_message': 'JSON Decode Error. Failed to parse JSON content'})
                        self.errorMsg = True
                        print(f"Failed to parse JSON content: {page}")
                        return
                else:
                    self.errorMessages['pages'].append({'page': page, 'error_message': 'No JSON block found in API response.'})
                    self.errorMsg = True
                    print(f"No JSON block found in content: {page}")
                    return

            # Fallback in case no valid response
            self.errorMessages['pages'].append({'page': page, 'error_message': '"No valid message content received from API.'})
            self.errorMsg = True
            print(f"No valid message content in page number {page}.")
            return

        except Exception as e:
            self.errorMessages['pages'].append({'page': page, 'error_message': f'An unexpected exception occured: {e}'})
            self.errorMsg = True
            print(f"Error in page number {page}: {e}")
            return