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
    def __init__(self, file, menuName):
        self.pdf = file
        self.menuName = menuName
        self.errorMsg = None
        self.key = settings.API_KEY
        
    def toImg(self):
        returnJson = {"description": self.menuName,
                "sections": []
            }
        responses = []
        try:
            with pdfplumber.open(self.pdf) as pdf:
                for i, page in enumerate(pdf.pages):
                    self.errorMsg = None
                    pilImage = page.to_image(resolution=300).original #In PIL format; need base64

                    buffer = BytesIO()
                    pilImage.save(buffer, format="PNG")
                    buffer.seek(0)

                    binImage = buffer.read()
                    b64Image = base64.b64encode(binImage).decode("utf-8")
                    print(f"Binary image created for page {i + 1}")

                    response = self.genResponse(b64Image, i+1)
                    if self.errorMsg is None:
                        responses.append((True, response))
                    else: #If an error message was created for this page, handle response gracefully
                        responses.append((False, ""))
                    print(f"Response from OpenAI: {responses[i]}")
                
                for page, response in enumerate(responses):
                    if response[0] is not False:
                        if isinstance(response[1], dict) and "sections" in response[1]:
                            page_data = response[1].get("sections", [])

                        else:
                            page_data = {"Error Message": f"Error in page number {page}: Iould not be parsed for menu data. It most likley did not have any menu content."}

                    else:
                        page_data = {"Error Message": f"Error in page number {page}: {self.errorMsg}."}

                    returnJson['sections'] = page_data
                return returnJson

        except Exception as e:
            print(f"Error converting to image: {e}")
            return json.dumps({"description": self.menuName,
                "Error Message": e
            })


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
                                "text": f"You are analyzing a menu that I need to turn into structured data. Provide a JSON object with these fields: 'page', 'section_name', 'menu_item', 'price', 'dietary_restriction', and 'description'. If you can't determine a field ensure its a valid JSON placeholden like 'null', except for sections. If you can't figure out a section name simply write down its section number (in the order that you reach it). Most importantly, I need the relationships to be accurate, so even if you can't find the section name of something ensure the relationships are correct, for example, still make sure that the correct menu_items are children of that unamed section. Another very important point is that for every section you find there might be multiple child sections. Make sure you still include those, and ensure that you are very confident when assigning a price, its ok if you leave it as 'null' if you're not sure. It also seems that you tend to interpret calories (cal.) as price, prices are always standalone digits or are preceded/followed by a currency symbol. ONLY RETURN VALID JSON",
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
            if hasattr(choice, 'message') and choice.message:
                content = choice.message.content
                json_match = re.search(r"```json\n(.*?)```", content, re.DOTALL)

                if json_match:
                    json_content = json_match.group(1)  # Extract the JSON part
                    json_content = json_content.strip() #Get rid of extra whitespace
                    print(f"json_content: {json_content}")
                    try:
                        parsed_content = json.loads(json_content)  # Parse the JSON content
                        return parsed_content
                    except json.JSONDecodeError:
                        self.errorMsg = f"Failed to parse JSON content for page number {page}."
                        print(f"Failed to parse JSON content: {json_content}")
                        return
                else:
                    self.errorMsg = f"No JSON block found in content for page number {page}."
                    print(f"No JSON block found in content: {content}")
                    return

            # Fallback in case no valid response
            self.errorMsg = f"No valid message content in page number {page}."
            print(f"No valid message content in page number {page}.")
            return

        except Exception as e:
            self.errorMsg = f"Error in page number {page}: {e}"
            print(f"Error in page number {page}: {e}")
            return