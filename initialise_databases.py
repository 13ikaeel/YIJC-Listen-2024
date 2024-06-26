####################################################
from sqlite3 import *
import hashlib

def calc_sha256_salted(data):
    data = 'LISTEN 2024' + str(data) + 'KJK_SWP'

    if isinstance(data,str):
        data = data.encode()
        
    return hashlib.sha256(data).hexdigest()
####################################################



def initialise(db_no):
    #db = connect(f"Ticketing{db_no}.db") uncomment when offline
    db = connect(f'Ticketing{db_no}.db') #comment off when offline
    c = db.cursor()

##########################################################################
    c.execute('''
    CREATE TABLE IF NOT EXISTS AllStudentsEmail(
        HashedEmail TEXT PRIMARY KEY NOT NULL,
        Booked INTEGER NOT NULL,
        PIN TEXT
    )''')


    emails = open('hashed_emails.txt')
    for email in emails.readlines():
        email = email.strip()
        c.execute('''
            INSERT INTO AllStudentsEmail
            (HashedEmail,Booked)
            VALUES(?,?)''', (email,0))
    emails.close()
##########################################################################


##########################################################################
    c.execute('''
    CREATE TABLE IF NOT EXISTS Tickets(
        TicketNo INTEGER PRIMARY KEY NOT NULL,
        Ticket_Hashed TEXT NOT NULL,
        Entry INTEGER NOT NULL,
        Reserved INTEGER NOT NULL
    )''')

    for ticket_no in range(1,901):
        if ticket_no < 10:
            ticket_hashed = f'00{ticket_no}'
        elif ticket_no < 100:
            ticket_hashed = f'0{ticket_no}'
        else:
            ticket_hashed = str(ticket_no)
            
        ticket_hashed = calc_sha256_salted(ticket_hashed)
        print(ticket_no, ticket_hashed)
        c.execute('''
            INSERT INTO Tickets (
            TicketNo, Ticket_Hashed, Entry, Reserved)\
            VALUES(?,?,0,0)''', (ticket_no,ticket_hashed))

    c.execute('''
        UPDATE Tickets
        SET Reserved=1
        WHERE TicketNo BETWEEN 1 AND 360
        OR TicketNo BETWEEN 801 AND 900;
    ''')
# c.execute(f'''UPDATE Tickets \
#         SET Reserved = 1 \
#         WHERE TicketNo BETWEEN 1 AND 899''')
#########################################################################

#########################################################################
    c.execute('''
        CREATE TABLE Bookings(
            Email TEXT NOT NULL,
            TicketNo INTEGER PRIMARY KEY,
            MC_Member TEXT,
            Message TEXT,
            Pin TEXT VARCHAR(6), 
            UNIQUE(Email, TicketNo),
            FOREIGN KEY (Email) 
            REFERENCES Students(Email),
            FOREIGN KEY (TicketNo)
            REFERENCES Tickets(TicketNo))''')

# c.execute('''INSERT INTO Bookings(\
#           Email, \
#           MC_Member, \
#           Message, \
#           Pin) VALUES('Placeholder for autoincrement', '', '', '000000')''')
# c.execute('''DELETE FROM Bookings WHERE Email = 'Placeholder for autoincrement';''')

# c.execute(f'''UPDATE SQLITE_SEQUENCE SET seq = {x} WHERE name = 'Bookings';''')

    db.commit()
    db.close()
####################################################
if __name__ == "__main__":
    initialise(0)
