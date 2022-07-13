from flask_login import UserMixin
from . import db

class Uzytkownicy(UserMixin, db.Model):
    __tablename__ = 'Uzytkownicy'
    id_uzytk = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    haslo = db.Column(db.String(100))
    pesel = db.Column(db.String(50))
    imie = db.Column(db.String(50))
    nazwisko = db.Column(db.String(50))
    telefon = db.Column(db.String(50))
    uprawnienia = db.Column(db.String(1))

    def get_id(self):
           return (self.id_uzytk)

class Portfele(db.Model):
    __tablename__ = 'Portfele'
    id_portfela = db.Column(db.Integer, primary_key=True)
    stan_konta = db.Column(db.Integer)
    dane_do_rozliczen = db.Column(db.String(50))
    wlasciciel = db.Column(db.Integer, db.ForeignKey('Uzytkownicy.id_uzytk'))
    nazwa = db.Column(db.String(50))

    def get_id(self):
           return (self.id_portfela)

class Oferty(db.Model):
    __tablename__ = 'Oferty'
    id_oferty = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(50))
    liczba_monet = db.Column(db.Integer)
    cena = db.Column(db.Numeric)

    def get_id(self):
           return (self.id_oferty)

class Ligi(db.Model):
    __tablename__ = 'Ligi'
    id_ligi = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(50))

    def get_id(self):
           return (self.id_ligi)

class Druzyny(db.Model):
    __tablename__ = 'Druzyny'
    id_druzyny = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(50))
    kraj = db.Column(db.String(50))
    stadion = db.Column(db.String(50))

class Mecze(db.Model):
    __tablename__ = 'Mecze'
    id_meczu = db.Column(db.Integer, primary_key=True)
    data_meczu = db.Column(db.Date)
    kurs_gospodarz = db.Column(db.Integer)
    kurs_gosc = db.Column(db.Integer)
    kurs_remis = db.Column(db.Integer)
    gospodarz = db.Column(db.Integer)
    gosc = db.Column(db.Integer)
    liga = db.Column(db.Integer)

    def get_id(self):
           return (self.id_meczu)

class Transakcje(db.Model):
    __tablename__ = 'Transakcje'
    id_transakcji = db.Column(db.Integer, primary_key=True)
    data_transakcji = db.Column(db.DateTime(timezone=True), server_default=db.func.curdate())
    stan_konta_przed = db.Column(db.Integer)
    stan_konta_po = db.Column(db.Integer)
    kwota = db.Column(db.Integer)
    rodzaj = db.Column(db.Integer, primary_key=True)
    portfel_transakcji = db.Column(db.Integer, primary_key=True)

    def get_id(self):
           return (self.id_transakcji)

class Wyniki(db.Model):
    __tablename__ = 'Wyniki'
    id_wyniku = db.Column(db.Integer, primary_key=True)
    mecz = db.Column(db.Integer)
    zwyciezca = db.Column(db.Integer)

    def get_id(self):
           return (self.id_wyniku)

class Zaklady(db.Model):
    __tablename__ = 'Zaklady'
    id_zakladu = db.Column(db.Integer, primary_key=True)
    typ = db.Column(db.Integer)
    monety_postawione = db.Column(db.Integer)
    status = db.Column(db.String(50))
    wygrana = db.Column(db.Integer)
    data_zakladu = db.Column(db.DateTime(timezone=True), server_default=db.func.curdate())
    portfel = db.Column(db.Integer)
    mecz = db.Column(db.Integer)

    def get_id(self):
           return (self.id_zakladu)