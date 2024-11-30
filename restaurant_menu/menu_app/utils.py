from tabula import read_pdf
import json
import pdfplumber
import pytesseract
import cv2
import numpy as np
# NO PARSE; JUST UPLOAD IMG TO GBT
class PdfParse:
    def __init__(self, file):
        self.pdf = file
        # return self.pdf
    
    def parse(self):
        try:
            data = {}
            
            # Open the PDF with pdfplumber
            with pdfplumber.open(self.pdf) as pdf:
                for i, page in enumerate(pdf.pages):
                    readable = bool(page.extract_text())  # Extract text from the page
                    print(f"Readable: {readable}")
                    if readable:
                        # pdf plumb
                        text = page.extract_text()
                        print(f"Page {i+1}: {text}")

                    else:
                        # OCR tessaract
                        # data = self.ocrParse(page)

                        # BREAK------------------------------
                        image = page.to_image(resolution=300).original
                        cv2Image = np.array(image)
                        cv2Image = cv2.cvtColor(cv2Image, cv2.COLOR_RGB2BGR)
                        grayImage = cv2.cvtColor(cv2Image, cv2.COLOR_BGR2GRAY)


                        # Performing OTSU threshold
                        ret, thresh1 = cv2.threshold(grayImage, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

                        # dilation parameter, bigger means less rectangle
                        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))

                        # Applying dilation on the threshold image
                        dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)

                        # Finding contours
                        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

                        # Creating a copy of image
                        im2 = grayImage.copy()


                        cnt_list=[]
                        for cnt in contours:
                            x, y, w, h = cv2.boundingRect(cnt)

                            # Drawing a rectangle on the copied image
                            rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 5)
                            cv2.circle(im2,(x,y),8,(255,255,0),8)

                            # Cropping the text block for giving input to OCR
                            cropped = im2[y:y + h, x:x + w]

                            # Apply OCR on the cropped image
                            text = pytesseract.image_to_string(cropped)

                            cnt_list.append([x,y,text])


                        # This list sorts text with respect to their coordinates, in this way texts are in order from top to down
                        sorted_list = sorted(cnt_list, key=lambda x: x[1])

                        # A text file is created 
                        file = open("recognized.txt", "w+")
                        file.write("")
                        file.close()


                        for x,y,text in sorted_list:
                            # Open the file in append mode
                            file = open("recognized.txt", "a")

                            # Appending the text into the file
                            file.write(text)
                            file.write("\n")

                            # Close the file
                            file.close()


                        # read image 
                        rgb_image = cv2.resize(im2, (0, 0), fx = 0.4, fy = 0.4)
                        dilation = cv2.resize(dilation, (0, 0), fx = 0.4, fy = 0.4)
                        #thresh1 = cv2.resize(thresh1, (0, 0), fx = 0.4, fy = 0.4)

                        # show the image, provide the window name first
                        #cv2.imshow('thresh1', thresh1)
                        cv2.imshow('dilation', dilation)
                        cv2.imshow('gray', gray)

                        # add wait key. window waits until the user presses a key
                        cv2.waitKey(0)
                        # and finally destroy/close all open windows
                        cv2.destroyAllWindows()

                        
                        

                    
                    # data.append(text)

            return data  # Return structured data as JSON

        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return json.dumps({"error": f"Error parsing PDF: {e}"})
    
    def ocrParse(self, page):
        # Convert the image into a numpy array and apply necessary preprocessing
        image = page.to_image(resolution=300).original
        cv2Image = np.array(image)
        cv2Image = cv2.cvtColor(cv2Image, cv2.COLOR_RGB2BGR)
        grayImage = cv2.cvtColor(cv2Image, cv2.COLOR_BGR2GRAY)

        # Thresholding to get binary image
        ret, thresh1 = cv2.threshold(grayImage, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        # Rectangular kernel for dilation
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

        # Find contours to identify areas of text
        contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Initialize list to store contours and text data
        cnt_list = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cropped = grayImage[y:y + h, x:x + w]

            # Use Tesseract to extract text from the cropped region
            text = pytesseract.image_to_string(cropped)

            # Get font size and other attributes
            text_size = len(text.split())  # Simple way to check for text length (you can enhance this with tesseract config)
            
            # Store the contour data, bounding box, and detected text
            cnt_list.append({
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "text": text.strip(),
                "text_size": text_size,
                "is_header": self.is_header(text, text_size)  # Custom header detection based on size or other factors
            })

        # Sort the text items by vertical position (y-coordinate)
        sorted_list = sorted(cnt_list, key=lambda x: x[1])
        print(f"Sorted list: {sorted_list}")
        # Organize the items into sections (headers + items)
        menu = self.organize_into_sections(sorted_list)
        txt = open("cv2Text.txt", "w+")
        txt.write("")
        txt.close

        for section in menu:
            txt = open("cv2Text.txt", "a")
            txt.write(section[0])
            if section[1]:
                for item in section[1]:
                    txt.write(f"\t{item}")
            txt.write("\n")
            txt.close

        
        print("JSON output saved successfully!")
        return menu

    def is_header(self, text, text_size):
        if text_size > 3:  # You can adjust this based on your menu's layout
            return True
        return False
    
    def organize_into_sections(self, sorted_list):
        menu_data = []  # Initialize an empty list for the 2D array
        current_section = None
        current_items = []

        for item in sorted_list:
            text = item['text']
            is_header = item['is_header']

            # If it's a header, store the current section and its items
            if is_header:
                if current_section:  # Add the previous section to the menu_data
                    menu_data.append([current_section, current_items])
                current_section = text
                current_items = []  # Reset the item list for the new section

            # Append menu items to the current section
            elif current_section:
                current_items.append({
                    "name": text,
                    "price": None,  # Can enhance price detection later
                    "dietary_restrictions": None  # Can add dietary restrictions logic
                })

        # Append the last section to menu_data
        if current_section:
            menu_data.append([current_section, current_items])

        return menu_data


    def extract_menu_items(self, text):
        """
        Custom logic to parse menu items from extracted text.
        Modify this function based on your menu format.
        """
        menu_items = []
        lines = text.split("\n")  # Split text into lines

        for line in lines:
            # Example: Assume lines are formatted like "Dish Name - Price"
            if "-" in line:
                parts = line.split("-", 1)
                item_name = parts[0].strip()
                item_price = parts[1].strip()

                # Add the parsed item to the list
                menu_items.append({"name": item_name, "price": item_price})

        return menu_items

    # def parse(self):
    #     try:
    #         tables = read_pdf(self.pdf, pages='all', multiple_tables=True, pandas_options={'header': None}, format="JSON")
    #         return tables
    #         parsed_data = [table.to_dict(orinet='records') for table in tables]
    #         return json.dumps(parsed_data)
    #     except Exception as e:
    #         print(f"Error parsing PDF: {e}")
    #         return None