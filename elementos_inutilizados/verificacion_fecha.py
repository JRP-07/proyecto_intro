from datetime import date
fecha_nacimiento = date(2009, 1, 1)
edad = date.today().year - fecha_nacimiento.year
if (date.today().month, date.today().day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
print (edad)

    