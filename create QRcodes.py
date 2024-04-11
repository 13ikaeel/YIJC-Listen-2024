import qrcode
from PIL import Image, ImageDraw, ImageFont  
from hashlib import *
from time import *

def calc_sha256_salted(data):
    data = 'LISTEN 2024' + str(data) + 'KJK_SWP'
    if isinstance(data,str):
        data = data.encode()
    return sha256(data).hexdigest()

def generate_qr(ticket_no):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(calc_sha256_salted(ticket_no))
    img = qr.make_image(fill_color='black', back_color="white").convert('RGB')

    # Add ticket number text onto the QR code image
    draw = ImageDraw.Draw(img)
    font_size = 24  # Adjust font size as needed
    font = ImageFont.truetype("arial.ttf", font_size)
    text = ticket_no
    text_width, text_height = draw.textsize(text, font)
    position = ((img.width - text_width) // 2, img.height - text_height - 10)
    draw.text(position, text, fill='black', font=font)

    img.save(f"static/Qrcodes_final/ticket_{ticket_no}.png")
    print(f'ticket_{ticket_no}.png created')

for i in range(1, 901):
    if i < 10:
        generate_qr(f'00{i}')
    elif i < 100:
        generate_qr(f'0{i}')
    else:
        generate_qr(str(i))
    
