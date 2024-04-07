import qrcode
from PIL import Image
from hashlib import *
from time import *
def calc_sha256_salted(data):
    data = 'LISTEN' + str(data) + '2024'
    if isinstance(data,str):
        data = data.encode()
    return sha256(data).hexdigest()
def generate_qr(ticket_no):
    logo = Image.open("static/Images/logo.png").resize((200, 200), Image.LANCZOS)
    qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(calc_sha256_salted(ticket_no))
    img = qr.make_image(fill_color= 'black' , back_color= "white").convert('RGB')
    img_w, img_h = img.size
    logo_w, logo_h = logo.size
    offset = ((img_w - logo_w) // 2, (img_h - logo_h) // 2)
    img.paste(logo, offset, mask=logo.split()[3] if logo.mode == 'RGBA' else None)
    img.save(f"static/Qrcodes/ticket_{ticket_no}.png")
    print(f'ticket_{ticket_no}.png created')
for i in range(1, 901):
    if i < 10:
        generate_qr(f'00{i}')
    elif i < 100:
        generate_qr(f'0{i}')
    else:
        generate_qr(str(i))
    
