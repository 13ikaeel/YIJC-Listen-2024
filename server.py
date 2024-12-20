from flask import* 
from sqlite3 import*
from hashlib import *
import random
from postmarker.core import PostmarkClient
postmark = PostmarkClient(server_token = '914d85ea-85fd-4024-9cc9-547d990b6643')
from initialise_databases import initialise


db_no = 0
def calc_sha256_salted(data):
    data = 'LISTEN' + str(data) + '2024'
    if isinstance(data,str):
        data = data.encode()
    return sha256(data).hexdigest()
def ticket_num(ticket_no):
    if ticket_no < 10:
        return f'00{ticket_no}'
    elif ticket_no < 100:
        return f'0{ticket_no}'
    else:
        return ticket_no
    

def remove_duplicate(email):
    global db_no
    db = connect(f"/home/yimc/YIJC-Listen-2024/Ticketing{db_no}.db") #comment when online
    c = db.cursor()

    c.execute('''
        SELECT * FROM Bookings 
        WHERE Email = ?
    ''', (email,))
    bookings = c.fetchall()[1:]

    tickets = []
    for book in bookings:
        ticket = book[1]
        tickets.append(ticket)

        c.execute('''
            DELETE FROM Bookings 
            WHERE TicketNo = ?
        ''', (ticket,))
        
        c.execute('''
            UPDATE Tickets 
            SET Reserved = 0 
            WHERE TicketNo = ?
        ''', (ticket,))

    db.commit()
    db.close()


def poke():
    global db_no
    db = connect(f"/home/yimc/YIJC-Listen-2024/Ticketing{db_no}.db")
    c = db.cursor()

    try:
        c.execute('''SELECT Email FROM Bookings''')
        email_list = c.fetchall()

        email_set = set()
        email_duplicate = set()
        for email in email_list:
            if email not in email_set:
                email_set.add(email)
            else:
                email_duplicate.add(email)

        if email_duplicate:
            for email in email_duplicate:
                remove_duplicate(email[0])
    
        c.execute('''
            INSERT INTO Bookings(Email, TicketNo, MC_Member, Message, Pin) 
            VALUES(?,?,?,?,?)
        ''', ("zhe_kai@students.edu,sg", "1000", " ", "", "ed3b45b4e6d6ab914d351b3afc3b08169f135d3109777c958a66d2493e537c31"))

        c.execute('''
            DELETE FROM Bookings 
            WHERE TicketNo = "1000"
        ''')
        db.commit()
        db.close()

    except Exception as e:
        print(e)
        create_new_db()
        db.commit()
        db.close()


def insert():
    global db_no
    db_2 = connect(f"/home/yimc/YIJC-Listen-2024/Ticketing{db_no+1}.db") #uncomment online
    c_2 = db_2.cursor()


    db = connect(f"/home/yimc/YIJC-Listen-2024/Ticketing{db_no}.db") #uncomment online
    c = db.cursor()

    c.execute('''
        SELECT * 
        FROM Bookings
    ''')
    bookings = c.fetchall()

    for book in bookings:
        print(f"BOOK: {book}")
        c_2.execute('''
            INSERT INTO Bookings(Email, TicketNo, MC_Member, Message, Pin) 
            VALUES(?,?,?,?,?)
        ''', book)

        c_2.execute('''
            UPDATE Tickets 
            SET Reserved = 1 
            WHERE TicketNo = ?
        ''', (book[1],))

    db_no += 1
    db.commit()
    db.close()
    db_2.commit()
    db_2.close()
    
def create_new_db():
    global db_no
    initialise(db_no + 1)
    insert()

members = [
    'EVERYONE!', 'Astrid', 'Ching Yee', 'Darius', 
    'Felicity', 'Insyirah', 'Jia Hao', 'Kayla', 
    'Min Rong', 'Nathanael', 'Nurin', 'Reyes', 
    'Thomas', 'Zhi Yi', 'Ayouni', 'Casey', 'Cayden', 
    'Chen Chen', 'Denisse', 'Julia', 'Kathleen', 
    'Nicholas', 'Nitiyaa', 'Rachel', 'Rui Xuan', 
    'Timothy', 'Vance', 'Wanyi', 'Yumeng', 'Zheng Rui', 
    'Beverly (alumni)', 'Joy (alumni)', 'Nathaniel (alumni)', 'Roxanne (alumni)'
    ]

    


app = Flask(__name__)
app.secret_key = 'mcyi'

#----------------------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    poke()
    global db_no
    # db = connect(f'Ticketing{db_no}.db') #uncomment for offline testing
    db = connect(f'/home/yimc/YIJC-Listen-2024/Ticketing{db_no}.db') #comment out for offline testing
    c = db.cursor()

    c.execute('''
        SELECT * 
        FROM Tickets 
        WHERE Reserved = 0
    ''')
    outOfTickets = c.fetchone() is None # Check if there are tickets left available
    db.close()

    return render_template('index.html', outOfTickets=outOfTickets, failedConnection=False)


#----------------------------------------------------------------------------------------------------------------------
@app.route('/validate-email', methods=['GET','POST'])
def validate():
    poke()
    global db_no
    email = request.form.get('email')
    email = email.lower()

    # db = connect(f'Ticketing{db_no}.db') #uncomment for offline testing
    db = connect(f'/home/yimc/YIJC-Listen-2024/Ticketing{db_no}.db') #comment out for offline testing
    c = db.cursor()

    # Check if the email address is a valid one (In the student emails table)
    c.execute('''
        SELECT * 
        FROM AllStudentsEmail
        WHERE HashedEmail = ?
    ''', (calc_sha256_salted(email),))
    exist = bool(c.fetchone())

    # Check if the email has already been used to book a ticket
    c.execute('''
        SELECT * 
        FROM Bookings
        WHERE Email = ?
    ''', (email,))
    duplicate = bool(c.fetchone())

    db.close()  

    #check if email exists in db and if the email has alr been used
    if exist: # if the email is valid
        if duplicate: # if the email has already been used to book a ticket
            flash("Invalid: Email already used")
            return redirect(url_for('index'))
        else:
            pin =  random.randint(100000, 999999)
            # db = connect(f'Ticketing{db_no}.db') #uncomment for offline testing
            db = connect(f'/home/yimc/YIJC-Listen-2024/Ticketing{db_no}.db') #comment out for offline testing
            c = db.cursor()

            c.execute('''
                UPDATE AllStudentsEmail 
                SET PIN = ? 
                WHERE HashedEmail = ?
            ''', (pin, calc_sha256_salted(email)))
            db.commit()
            db.close()
        
            # yag = yagmail.SMTP("yimusiciansclub@gmail.com", "sebi eyvp igyl vqfa")
            postmark.emails.send(
                From = 'listen@yimusicians.org',
                To = f'{email}',
                Subject = 'PIN for LISTEN 2024 Ticket',
                HtmlBody = f'Here is your pin: <br><br>{pin}'
            )
            # yag.send(f"{email}", "LISTEN 2024 concert", f"Here is your pin {pin}")
            return render_template("validating.html", details=[email, '', ''],email=email, members=members)
    else:
        flash("Invalid email")
        return redirect(url_for('index'))



#----------------------------------------------------------------------------------------------------------------------
@app.route('/booking/confirmation', methods=['POST','GET'])
def confirmation():
    poke()
    global db_no
    email = request.form.get('email')
    print(email)
    print(calc_sha256_salted(email))
    pin = request.form.get('pin')

    # db = connect(f'Ticketing{db_no}.db') #uncomment for offline testing
    db = connect(f'/home/yimc/YIJC-Listen-2024/Ticketing{db_no}.db') #comment out for offline testing
    c = db.cursor()

    c.execute('''
        SELECT PIN 
        FROM AllStudentsEmail 
        WHERE HashedEmail = ?
    ''', (calc_sha256_salted(email),))
    correct_pin = c.fetchone()[0]

    db.close()  # Corrected db.close() by adding parentheses

    #check if the pin keyed in is correct
    if pin == correct_pin:
        return render_template("confirmation.html", details=[email, '', ''],email=email, members=members)
    else:
        flash("Incorrect pin")
        return render_template("validating.html", details=[email, '', ''],email=email, members=members)


#----------------------------------------------------------------------------------------------------------------------
@app.route('/booking/success', methods = ['POST'])
def success():
    global db_no
    poke()
    email = request.form.get('email')
    member = request.form.get('member')
    message = request.form.get('message')
    pin = request.form.get('pin')

    # db = connect(f"Ticketing{db_no}.db") #uncomment for offline testing
    db = connect(f'/home/yimc/YIJC-Listen-2024/Ticketing{db_no}.db') #comment out for offline testing
    c = db.cursor()

    c.execute('''
        SELECT * 
        FROM Bookings 
        WHERE Email = ?
    ''', (email,))
    duplicate = c.fetchone()
    db.close()

    if duplicate:
        flash("Invalid: Email already used")
        return redirect(url_for('index'))
    
    if message and not member: # they much either choose 'everyone' or someone to send a message
        flash("Please indicate a member to send a shoutout")
        return render_template('confirmation.html', email = email, message = message, pin=pin, members = members, error = '*Please indicate a member to send a shoutout')
    
    else:
        # Booking is successful and the database is updated

        # db = connect(f'Ticketing{db_no}.db') #uncomment for offline testing
        db = connect(f'/home/yimc/YIJC-Listen-2024/Ticketing{db_no}.db') #comment out for offline testing
        c = db.cursor()

        c.execute('''
            SELECT TicketNo 
            FROM Tickets 
            WHERE Reserved = 0
        ''')
        available = c.fetchone()[0]
        print(available)

        c.execute('''
            INSERT INTO Bookings(Email, TicketNo, MC_Member, Message, Pin) 
            VALUES(?,?,?,?,?)
        ''', (email, available ,member, message, calc_sha256_salted(pin)))

        c.execute('''
            SELECT TicketNo 
            FROM Bookings 
            WHERE Email = ?
        ''', (email,))
        ticket_no = c.fetchone()

        c.execute('''
            UPDATE Tickets 
            SET Reserved = 1 
            WHERE TicketNo = ?
        ''', (ticket_no[0],))

        db.commit()
        db.close()

        # generate_qr(ticket_no)
        try:
            # yag = yagmail.SMTP("yimusiciansclub@gmail.com", "sebi eyvp igyl vqfa")
            email = postmark.emails.Email(
                From = 'listen@yimusicians.org',
                To = f'{email}',
                Subject = 'LISTEN 2024 Concert Ticket',
                HtmlBody = '''
                    <p>
                    Date: 26 April 2024 Friday<br>
                    Time: 7pm<br>
                    Venue: YIJC Hall<br>
                    </p>
                    <p>
                    If you wish to, you can still collect a hard copy ticket from us at our collection booth, or simply use this QR code for admission on show day.<br>
                    </p>
                    <p>
                    Terms and Conditions:
                    <ol>
                        <li>Damaged QR codes and wristbands will not be accepted for admission or readmission.</li>
                        <li>This event is free standing.</li>
                        <li>MC reserves the right to refuse the admission or evict any person whose conduct is disorderly or inappropriate or poses a security threat.</li>
                        <li>MC may postpone, cancel or interrupt the event due to dangerous situations or any cause beyond reasonable control.</li>
                        <li>As part of security and adherence to college rules, all bags will be checked before entering the venue.</li>
                    </ol>
                    </p>
             '''
            )
            email.attach(f'/home/yimc/YIJC-Listen-2024/static/QRcodes/ticket_{ticket_num(ticket_no[0])}.png') #uncomment when offline
            email.send()

            return render_template('success.html')
        
        except Exception as error:	
            print(f"error message: {error}")
            return render_template("index.html", failedConnection=True, outOfTickets=False)

#----------------------------------------------------------------------------------------------------------------------
@app.route('/resend-ticket', methods=["GET","POST"])
def resend_ticket():
    poke()
    return render_template('resend_ticket.html')

#----------------------------------------------------------------------------------------------------------------------
@app.route('/resend-ticket/success', methods=["GET","POST"])
def resend_ticket_success():
    global db_no
    poke()
    email = request.form.get('email')
    pin = request.form.get('pin')

    # db = connect(f'Ticketing{db_no}.db') #uncomment for offline testing
    db = connect(f'/home/yimc/YIJC-Listen-2024/Ticketing{db_no}.db') #comment out for offline testing
    c = db.cursor()

    hashed_email = str(calc_sha256_salted(email))
    c.execute('''
        SELECT * 
        FROM AllStudentsEmail
        WHERE HashedEmail = ?
    ''', (hashed_email,))

    exist = bool(c.fetchone())
    c.execute('''
        SELECT TicketNo 
        FROM Bookings 
        WHERE pin =? AND email = ?
        ''', (calc_sha256_salted(pin), email))
    TicketNo = c.fetchone()

    db.close()

    if exist:
        if TicketNo:
            try:
                email = postmark.emails.Email(
                    From = 'listen@yimusicians.org',
                    To = f'{email}',
                    Subject = 'LISTEN 2024 Concert Ticket',
                    HtmlBody = '''
                    <p>
                    Date: 26 April 2024 Friday<br>
                    Time: 7pm<br>
                    Venue: YIJC Hall<br>
                    </p>
                    <p>
                    If you wish to, you can still collect a hard copy ticket from us at our collection booth, or simply use this QR code for admission on show day.<br>
                    </p>
                    <p>
                    Terms and Conditions:
                    <ol>
                        <li>Damaged QR codes and wristbands will not be accepted for admission or readmission.</li>
                        <li>This event is free standing.</li>
                        <li>MC reserves the right to refuse the admission or evict any person whose conduct is disorderly or inappropriate or poses a security threat.</li>
                        <li>MC may postpone, cancel or interrupt the event due to dangerous situations or any cause beyond reasonable control.</li>
                        <li>As part of security and adherence to college rules, all bags will be checked before entering the venue.</li>
                    </ol>
                    </p>
             '''
                )
                email.attach(f'/home/yimc/YIJC-Listen-2024/static/QRcodes/ticket_{ticket_num(TicketNo[0])}.png') #uncomment when offline
                # email.attach(f'static/QRcodes/ticket_{ticket_num(TicketNo[0])}.png') #comment off Online
                email.send()
                
                return render_template("resend_ticket_success.html")
            except Exception as error:
                print(f"error message: {error}")    
                return render_template("index.html", failedConnection=True, outOfTickets=False)
        else:
            flash("Email is Not Found...Sign Up")
            return redirect(url_for('resend_ticket'))
    else:
        flash("Email is Invalid")
        return redirect(url_for('resend_ticket'))

#----------------------------------------------------------------------------------------------------------------------
@app.route("/contact")
def contact():
    poke()
    return render_template("contact.html")


@app.route("/contact_success", methods = ['GET', 'POST'])
def contact_success():
    poke()
    name = request.form.get('Name')
    email = request.form.get("Email")
    text = request.form.get("Text")
    topic = request.form.get("request")
    postmark.emails.send(
        From = 'listen@yimusicians.org',
        To  = 'enquiries@yimusicians.org',
        Subject = f'{topic}',
        HtmlBody = f'{text}\n\n from: {name}, {email}'
    )

    return render_template("contact_success.html")


if __name__ == '__main__':
    app.run(debug=False, port=5023)

