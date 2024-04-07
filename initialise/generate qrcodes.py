####################################################
#make sure to: pip install qrcode
#make sure to: pip install pillow
#make sure to have a folder call "QRcodes"

import os
import qrcode
from PIL import Image
from sqlite3 import *
####################################################
ticketing_path = os.path.join(os.path.dirname(__file__), '../Ticketing.db')
db = connect(ticketing_path)
c = db.cursor()

numbers = (2,5,1,3)
letters = ('M', 'U', 'S', 'I', 'C')
c.execute('''SELECT Ticket_Hashed FROM Tickets''')
counter = 1

for ticket_hashed in c.fetchall():
    checksum = 0
    for i in range(4):
        checksum += ord(ticket_hashed[0][::16][i]) * numbers[i]

    checksum = letters[checksum%5]
    
    size = 200
    logo = Image.open("./logo.png").resize((size,size), Image.LANCZOS)

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )

    qr.add_data(ticket_hashed[0] + checksum)
    img_qr = qr.make_image(fill_color= 'black' , back_color= "white").convert('RGB')
    offset = ((img_qr.size[0] - size) // 2, (img_qr.size[1] - size) // 2)
    img_qr.paste(logo, offset, mask=logo.split()[3] if logo.mode == 'RGBA' else None)

    image_path = os.path.join(os.path.dirname(__file__), f"../static/QRcodes/{counter}.png")  
    
    img_qr.save(image_path)

    counter += 1

db.close()