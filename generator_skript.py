import numpy as np
import random
from faker import Faker
from datetime import date
import random
import csv

def load_names(path):
    names = []
    probabilities = []
    with open(path, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';',)
        for row in csv_reader:
            names.append(row[0])
            probabilities.append(row[1])
    probabilities = [float(i.replace(',', '.')) for i in probabilities]
    probabilities[0] = probabilities[0] + (1-sum(probabilities))
    return(names,probabilities)
def load_prijmenis(path):
    last_names_male = []
    last_names_female = []
    with open(path, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';',)
        for row in csv_reader:
            prijmeni = row[0]
            if prijmeni.endswith("á"):
                last_names_female.append(prijmeni)
            else:
                last_names_male.append(prijmeni)
    return(last_names_male,last_names_female)

class MyFakes():
    first_names_male, first_names_male_probabilities = load_names('first_names_male.csv')
    first_names_female, first_names_female_probabilities = load_names('first_names_female.csv')
    last_names_male, last_names_female = load_prijmenis('prijmeni.csv')
    krevni_skupiny= [
        '0-',
        '0-,DU+',
        '0+',
        '0RHDWV',
        'A-',
        'A-,DU+',
        'A+',
        'A1-',
        'A1-,DU+',
        'A1+',
        'A1B-',
        'A1B-,DU+',
        'A1B+',
        'A1BRHWV',
        'A1RHDWV',
        'A2-',
        'A2-,DU+',
        'A2+',
        'A2B-',
        'A2B-,DU+',
        'A2B+',
        'A2BRHWV',
        'A2RHDWV',
        'AB-',
        'AB-,DU+',
        'AB+',
        'ABRHDWV',
        'ARHDWV',
        'B-',
        'B-,DU+',
        'B+',
        'BRHDWV']
    pojistovny = [205, 207, 213, 201, 111, 209, 300]
    vzdelani = ['základní', 'středoškolské', 'vysokoškolské']
    tituly = ['Bc.', 'Ing.', 'Mgr.', 'PhD.', 'MUDr.', 'JUDr.']
class Pacient():
    def __init__(self):
        self.rc, self.jmeno, self.prijmeni = '', '', ''
        fake = Faker("cs_CZ")

        self.telefon = fake.phone_number()
        self.adresa = fake.address().replace('\n', ', ')
        self.datum_narozeni_datetime = fake.date_of_birth(maximum_age = 100)
        self.datum_narozeni = str(self.datum_narozeni_datetime.day)+"."+str(self.datum_narozeni_datetime.month) + "." + str(self.datum_narozeni_datetime.year)
        self.pojistovna = str(np.random.choice(MyFakes.pojistovny, 1)[0])
        self.krevni_skupina = np.random.choice(MyFakes.krevni_skupiny, 1)[0]
        
        if (date.today()-self.datum_narozeni_datetime).days/365<14:
            self.vzdelani = 'žádné'
            self.titul = ''
        elif (date.today()-self.datum_narozeni_datetime).days/365<17:
            self.vzdelani = 'základní'
            self.titul = ''
        else:
            self.vzdelani = np.random.choice(MyFakes.vzdelani, p= ['0.1', '0.6', '0.3'])
        if self.vzdelani == 'vysokoškolské':
            self.titul = np.random.choice(MyFakes.tituly, 1)[0]
        else:
            self.titul = ''
    def make_SQL_insert(self, tableName):
            sql = "INSERT INTO {} VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\");".format(tableName, self.rc, self.jmeno, self.prijmeni, self.titul, self.datum_narozeni, self.pojistovna, self.vzdelani, self.krevni_skupina, self.adresa, self.telefon)
            return(sql)
class Pacient_muz(Pacient):
    def __init__(self):
        Pacient.__init__(self)

        self.jmeno = np.random.choice(MyFakes.first_names_male, p=MyFakes.first_names_male_probabilities)
        self.prijmeni = np.random.choice(MyFakes.last_names_male)
        
        self.rc = str(self.datum_narozeni_datetime.year)[2:4]+str(self.datum_narozeni_datetime.month).zfill(2)+str(self.datum_narozeni_datetime.day).zfill(2)+ str(random.randint(1, 999)).zfill(3)
        if int(self.rc)%11>0 and int(self.rc)%11!=10:
            self.rc = self.rc + str(int(self.rc)%11)
        else:
            self.rc = self.rc + '0'
        self.rc = self.rc[0:6]  + '/' +self.rc[6:]
class Pacient_zena(Pacient):
    def __init__(self):
        Pacient.__init__(self)
        self.jmeno = np.random.choice(MyFakes.first_names_female, p=MyFakes.first_names_female_probabilities)
        self.prijmeni = np.random.choice(MyFakes.last_names_female)
        self.rc = str(self.datum_narozeni_datetime.year)[2:4]+str(self.datum_narozeni_datetime.month+50).zfill(2)+str(self.datum_narozeni_datetime.day).zfill(2)+ str(random.randint(1, 999)).zfill(3)
        if int(self.rc)%11>0 and int(self.rc)%11!=10:
            self.rc = self.rc + str(int(self.rc)%11)
        else:
            self.rc = self.rc + '0'
        self.rc = self.rc[0:6]  + '/' +self.rc[6:]

def generovat_SQL_inserty(pocet, jmeno_tabulky):
    SQL_inserty = []
    for i in range(pocet):
        if random.uniform(0, 1)>0.5:
            novy_pacient = Pacient_muz()
        else:
            novy_pacient = Pacient_zena()
        SQL_inserty.append(novy_pacient.make_SQL_insert(jmeno_tabulky))
    return(SQL_inserty)
def write_to_txt(inserty, filename = 'inserts.txt'):
    with open(filename, 'w', encoding="utf-8") as f:
        for item in inserty:
            f.write("%s\n" % item)

if __name__=="__main__":
    inserty = generovat_SQL_inserty(1000, "Pacienti")
    write_to_txt(inserty, 'inserts.txt')
    t

