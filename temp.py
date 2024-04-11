# from sqlite3 import *


# db = connect("Ticketing.db")
# c = db.cursor()

# c.execute('''
# 	DELETE FROM Bookings
# 	WHERE Email=?
# ''',('mikaeel_abdul_karim@students.edu.sg',))

# db.commit()
# db.close()

file = open('MC_Members.txt')
members = []
for line in file:
    members.append(line.strip())
    
print(members)