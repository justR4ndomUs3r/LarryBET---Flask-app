from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from . import db
from .models import *

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    portfele = db.session.query(Portfele).filter(Portfele.wlasciciel == current_user.id_uzytk).all()
    oferty = db.session.query(Oferty).all()
    zaklady = db.session.execute('''SELECT gosp.nazwa AS gospodarz, gosc.nazwa AS gosc, z.typ, z.monety_postawione, m.data_meczu, z.`status`, 
    m.kurs_gospodarz,m.kurs_gosc,m.kurs_remis, z.wygrana, w.zwyciezca  FROM portfele p 
            INNER JOIN zaklady z ON p.id_portfela = z.portfel 
            INNER JOIN mecze m ON z.mecz = m.id_meczu
            INNER JOIN druzyny gosp ON m.gospodarz = gosp.id_druzyny
            INNER JOIN druzyny gosc ON m.gosc=gosc.id_druzyny
            LEFT JOIN wyniki w ON m.id_meczu = w.mecz
            WHERE p.wlasciciel = :x ;''', {"x":current_user.id_uzytk})
    bets = [zaklad for zaklad in zaklady]
    return render_template('profile.html', name=current_user.imie, nazwisko=current_user.nazwisko, 
        pesel=current_user.pesel, telefon=current_user.telefon, portfele = portfele, oferty = oferty,
        zaklady=bets)

@main.route('/del_user', methods=['POST'])
@login_required
def del_user():
    id_uzytk = request.form.get('id_uzytk')
    if current_user.id_uzytk == id_uzytk:
        db.session.execute('''DELETE FROM uzytkownicy WHERE id_uzytk = :x;''', {"x":id_uzytk} )
        db.session.commit()
        return redirect(url_for('auth.logout'))
    db.session.execute('''DELETE FROM uzytkownicy WHERE id_uzytk = :x;''', {"x":id_uzytk} )
    db.session.commit()
    return redirect(url_for('main.bet'))


@main.route('/del_vallet', methods=['POST'])
@login_required
def del_vallet():
    id_portfela = request.form.get('id_portfela')
    aktywne_zaklady = db.session.execute('''SELECT * FROM portfele p INNER JOIN zaklady z ON p.id_portfela = z.portfel
                                            WHERE p.id_portfela = :x AND z.`status` = 'N';''', {"x":id_portfela} ).first()
    stan_konta = db.session.query(Portfele).filter(Portfele.id_portfela == id_portfela).first().stan_konta

    if aktywne_zaklady:
        flash('Nie możesz usunąć portfela, który bierze udział w aktywnych zakładach.')
        return redirect(url_for('main.profile'))

    elif int(stan_konta) > 0:
        flash('Nie możesz usunąć portfela, na któym posiadasz LarryCoin.')
        return redirect(url_for('main.profile'))
    else:
        db.session.execute('''DELETE FROM portfele WHERE id_portfela = :x;''', {"x":id_portfela} )
        db.session.commit()
        return redirect(url_for('main.profile'))

@main.route('/doladuj', methods=['POST'])
@login_required
def doladuj():
    id_vallet = request.form.get('vallets')
    if not id_vallet: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Stwórz portfel przed doładowaniem')
        return redirect(url_for('main.profile'))
    id_oferta = request.form.get('oferta')
    ile = int(request.form.get('ile'))
    monety = int(db.session.query(db.func.larrybet.licz_monety(id_oferta, ile)).first()[0])
    kwota =  int(db.session.query(db.func.larrybet.licz_cene(id_oferta, ile)).first()[0])
    rodzaj = db.session.query(Oferty).filter(Oferty.id_oferty == id_oferta).first().nazwa
    stan_konta_przed = db.session.query(Portfele).filter(Portfele.id_portfela == id_vallet).first().stan_konta
    if rodzaj == 'SPRZEDAZ':
        if stan_konta_przed - monety >= 0:
            stan_konta_po = stan_konta_przed - monety
            db.session.execute('''CALL doladuj_konto(:x, :y)''', {"x":-monety, "y":id_vallet})
        else:
            flash('Nie masz wystarczająco monet na tym portfelu')
            return redirect(url_for('main.profile'))
    else:
        stan_konta_po = stan_konta_przed + monety
        db.session.execute('''CALL doladuj_konto(:x, :y)''', {"x":monety, "y":id_vallet})
        

    new_trans = Transakcje(
        stan_konta_przed=stan_konta_przed, 
        stan_konta_po=stan_konta_po, 
        kwota=kwota,
        rodzaj=id_oferta, 
        portfel_transakcji=id_vallet)

    db.session.add(new_trans)
    db.session.commit()
    
    db.session.commit()
    return redirect(url_for('main.profile'))


@main.route('/add_account_post', methods=['POST'])
@login_required
def add_account_post():
    name = request.form.get('vallet')
    account = request.form.get('account_number')
    owner = current_user.id_uzytk

    vallet = Portfele.query.filter_by(nazwa=name, wlasciciel=owner).first() # if this returns a user, then the email already exists in database

    if vallet: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Posiadasz już portfel o tej nazwie.')
        return redirect(url_for('main.profile'))

    new_vallet = Portfele(stan_konta = 0, dane_do_rozliczen = account, wlasciciel = owner, nazwa = name)

    db.session.add(new_vallet)
    db.session.commit()
    return redirect(url_for('main.profile'))

@main.route('/data_post', methods=['POST'])
@login_required
def data_post():
    name = request.form.get('change_name')
    nazwisko = request.form.get('change_nazwisko')
    pesel = request.form.get('change_pesel')
    telefon = request.form.get('change_telefon')
    new_password = request.form.get('new_password')
    old_password = request.form.get('old_password')

    if not check_password_hash(current_user.haslo, old_password):
        flash('Błędne hasło.')
        return redirect(url_for('main.profile'))
    current_user.imie = name
    current_user.nazwisko = nazwisko
    current_user.pesel = pesel
    current_user.telefon = telefon
    current_user.haslo = generate_password_hash(new_password, method='sha256')
    db.session.commit()
    return redirect(url_for('main.profile'))

@main.route('/bet')
@login_required
def bet():
    druzyny = db.session.query(Druzyny).all()
    portfele = db.session.query(Portfele).filter(Portfele.wlasciciel == current_user.id_uzytk).all()
    ligi = db.session.query(Ligi).all()
    statement = db.session.execute('''
    SELECT m.id_meczu, m.data_meczu, m.kurs_gospodarz, m.kurs_gosc, m.kurs_remis, gosp.nazwa AS gospodarz, 
    gosp.kraj AS kraj, gosp.stadion AS stadion, gosc.nazwa AS gosc, l.nazwa AS liga, w.zwyciezca 
    FROM mecze m 
    INNER JOIN druzyny gosp ON m.gospodarz = gosp.id_druzyny 
    INNER JOIN druzyny gosc ON m.gosc = gosc.id_druzyny
    INNER JOIN ligi l ON m.liga = l.id_ligi
	 LEFT JOIN wyniki w ON m.id_meczu=w.mecz
     ORDER BY data_meczu;
    ''')
    mecze = [mecz for mecz in statement]
    return render_template('bet.html', ligi = ligi, mecze = mecze, portfele = portfele, druzyny = druzyny)


@main.route('/bet_post', methods=['POST'])
@login_required
def bet_post():
    id_meczu = request.form.get('id_meczu')
    if current_user.uprawnienia == 'K':
        typ = request.form.get('typ')
        portfel_id = request.form.get('vallets')
        kwota = int(request.form.get('kwota'))
        portfel = db.session.query(Portfele).filter(Portfele.id_portfela == portfel_id).first()

        if not portfel: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Nie można obstawić zakładu bez stworzonego portfela')
            return redirect(url_for('main.profile'))

        if kwota > portfel.stan_konta:
            flash('Nie masz wystarczająco monet na tym portfelu')
            return redirect(url_for('main.bet'))
        elif kwota > 1:
            new_bet = Zaklady(
                typ=typ, 
                monety_postawione=kwota, 
                status='N', 
                wygrana=0, 
                portfel=portfel_id, 
                mecz=id_meczu)

            db.session.add(new_bet)
            db.session.commit()

            portfel.stan_konta = portfel.stan_konta - kwota
            db.session.commit()
        return redirect(url_for('main.bet'))
    else:
        win = request.form.get('win')
        mecz = db.session.query(Mecze).filter(Mecze.id_meczu == id_meczu).first()
        new_result = Wyniki(
                mecz=id_meczu, 
                zwyciezca=win)

        db.session.add(new_result)
        db.session.commit()

        zaklady = db.session.query(Zaklady).filter(Zaklady.mecz == id_meczu).all()
        for zaklad in zaklady:
            portfel = db.session.query(Portfele).filter(Portfele.id_portfela == zaklad.portfel).first()
            typ = int(zaklad.typ)
            winner = int(win)
            if typ == winner:
                if winner == 0:
                    zaklad.wygrana = zaklad.monety_postawione * mecz.kurs_remis
                elif winner == 1:
                    zaklad.wygrana = zaklad.monety_postawione * mecz.kurs_gospodarz
                elif winner == 2:
                    zaklad.wygrana = zaklad.monety_postawione * mecz.kurs_gosc
                portfel.stan_konta = portfel.stan_konta + zaklad.wygrana
            zaklad.status = 'R'
            db.session.commit()
        return redirect(url_for('main.bet'))

@main.route('/addbet_post', methods=['POST'])
@login_required
def addbet_post():
    data_meczu = request.form.get('data_meczu')
    kurs_gospodarz = request.form.get('kurs_gospodarz')
    kurs_gosc = request.form.get('kurs_gosc')
    kurs_remis = request.form.get('kurs_remis')
    gospodarz_id = request.form.get('gospodarz')
    gosc_id = request.form.get('gosc')
    liga = request.form.get('liga')
    if gospodarz_id == gosc_id:
        flash('Druzyna nie moze grac z samą sobą')
        return redirect(url_for('main.bet'))
    gospodarz = db.session.execute( '''SELECT l.id_ligi FROM druzyny d 
                INNER JOIN ligi_druzyny ld ON d.id_druzyny=ld.id_druzyny
                INNER JOIN ligi l ON l.id_ligi=ld.id_ligi
                WHERE d.id_druzyny = :x;''', {"x":gospodarz_id})
    gosc = db.session.execute( '''SELECT l.id_ligi FROM druzyny d 
                INNER JOIN ligi_druzyny ld ON d.id_druzyny=ld.id_druzyny
                INNER JOIN ligi l ON l.id_ligi=ld.id_ligi
                WHERE d.id_druzyny = :x;''', {"x":gosc_id})
    flag = False
    for l in gospodarz:
        if l[0] == int(liga):
            flag = True
    if not flag:
        flash('Gospodarz nie należy do wybranej ligi')
        return redirect(url_for('main.bet'))
    flag = False
    for l in gosc:
        if l[0] == int(liga):
            flag = True
    if not flag:
        flash('Gosc nie należy do wybranej ligi')
        return redirect(url_for('main.bet'))
    
    new_mecz = Mecze(
                data_meczu=data_meczu, 
                kurs_gospodarz=kurs_gospodarz,
                kurs_gosc=kurs_gosc,
                kurs_remis=kurs_remis,
                gospodarz=gospodarz_id,
                gosc=gosc_id,
                liga=liga)

    db.session.add(new_mecz)
    db.session.commit()
    return redirect(url_for('main.bet'))

@main.route('/database')
@login_required
def database_reload():
    return redirect(url_for('main.bet'))

@main.route('/database', methods=['POST'])
@login_required
def database():
    choice = request.form.get('choice')
    if choice == 'Pracownicy':
        pracownicy = db.session.query(Uzytkownicy).filter(Uzytkownicy.uprawnienia == 'M').all()
        return render_template('database.html', choice = choice, pracownicy=pracownicy)

    if choice == 'Klienci':
        klienci = db.session.query(Uzytkownicy).filter(Uzytkownicy.uprawnienia == 'K').all()
        return render_template('database.html', choice = choice, klienci=klienci)

    if choice == 'Transakcje':
        statement = db.session.execute('''
            SELECT t.id_transakcji, t.data_transakcji, t.stan_konta_przed, t.stan_konta_po, o.nazwa, t.kwota, 
            p.dane_do_rozliczen, u.imie, u.nazwisko, u.pesel, u.telefon FROM transakcje t
            LEFT JOIN oferty o ON t.rodzaj = o.id_oferty
            LEFT JOIN portfele p ON t.portfel_transakcji = p.id_portfela
            LEFT JOIN uzytkownicy u ON p.wlasciciel = u.id_uzytk;''')
        transakcje = [transakcja for transakcja in statement]
        return render_template('database.html', choice = choice, transakcje=transakcje)

    if choice == 'Oferty':
        oferty = db.session.query(Oferty).all()
        return render_template('database.html', choice = choice, oferty=oferty)

    if choice == 'Druzyny':
        druzyny = db.session.query(Druzyny).all()
        return render_template('database.html', choice = choice, druzyny=druzyny)

    if choice == 'Ligi':
        ligi = db.session.query(Ligi).all()
        statement = db.session.execute('''SELECT d.id_druzyny, d.nazwa AS zespol, d.kraj, d.stadion, l.id_ligi, l.nazwa AS liga FROM druzyny d
                INNER JOIN ligi_druzyny ld ON d.id_druzyny=ld.id_druzyny
                INNER JOIN ligi l ON l.id_ligi = ld.id_ligi;''')
        ld = [ld for ld in statement]
        druzyny = db.session.query(Druzyny).all()
        return render_template('database.html', choice = choice, ligi=ligi, ld=ld, druzyny=druzyny)

    return render_template('database.html', choice = choice)

@main.route('/add_worker', methods=['POST'])
@login_required
def add_worker():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    nazwisko = request.form.get('nazwisko')
    pesel = request.form.get('pesel')
    telefon = request.form.get('telefon')

    user = Uzytkownicy.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Istnieje konto o podanym adresie email')
        return redirect(url_for('main.bet'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = Uzytkownicy(
        email=email, 
        haslo=generate_password_hash(password, method='sha256'), 
        pesel=pesel, 
        imie=name, 
        nazwisko=nazwisko, 
        telefon=telefon, 
        uprawnienia='M')

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('main.bet'))

@main.route('/oferta', methods=['POST'])
@login_required
def oferta():
    check = request.form.get('check')
    if check == 'dodaj':
        nazwa = request.form.get('nazwa')
        liczba_monet = request.form.get('liczba_monet')
        cena = request.form.get('cena')

        oferta = Oferty.query.filter_by(nazwa=nazwa).first() # if this returns a user, then the email already exists in database

        if oferta: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Istnieje oferta o podanej nazwie')
            return redirect(url_for('main.bet'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_oferta = Oferty(
            nazwa=nazwa, 
            liczba_monet=liczba_monet, 
            cena=cena)

        # add the new user to the database
        db.session.add(new_oferta)
        db.session.commit()
        return redirect(url_for('main.bet'))
    elif check == 'usun':
        id_oferty = request.form.get('id_oferty')
        db.session.execute('''DELETE FROM oferty WHERE id_oferty = :x;''', {"x":id_oferty} )
        db.session.commit()
        return redirect(url_for('main.bet'))
    else:
        return redirect(url_for('main.bet'))

@main.route('/team', methods=['POST'])
@login_required
def team():
    check = request.form.get('check')
    if check == 'dodaj':
        nazwa = request.form.get('nazwa')
        kraj = request.form.get('kraj')
        stadion = request.form.get('stadion')

        team = Druzyny.query.filter_by(nazwa=nazwa).first() # if this returns a user, then the email already exists in database

        if team: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Istnieje drużyna o podanej nazwie')
            return redirect(url_for('main.bet'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_druzyna = Druzyny(
            nazwa=nazwa, 
            kraj=kraj, 
            stadion=stadion)

        # add the new user to the database
        db.session.add(new_druzyna)
        db.session.commit()
        return redirect(url_for('main.bet'))
    elif check == 'usun':
        id_druzyny = request.form.get('id_druzyny')
        db.session.execute('''DELETE FROM druzyny WHERE id_druzyny = :x;''', {"x":id_druzyny} )
        db.session.commit()
        return redirect(url_for('main.bet'))
    else:
        return redirect(url_for('main.bet'))


@main.route('/liga', methods=['POST'])
@login_required
def liga():
    check = request.form.get('check')
    if check == 'dodaj':
        nazwa = request.form.get('nazwa')
        liga = Ligi.query.filter_by(nazwa=nazwa).first() # if this returns a user, then the email already exists in database

        if liga: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Istnieje liga o podanej nazwie')
            return redirect(url_for('main.bet'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_liga = Ligi(
            nazwa=nazwa)

        # add the new user to the database
        db.session.add(new_liga)
        db.session.commit()
        return redirect(url_for('main.bet'))
    elif check == 'usun':
        id_ligi = request.form.get('id_ligi')
        db.session.execute('''DELETE FROM ligi WHERE id_ligi = :x;''', {"x":id_ligi} )
        db.session.commit()
        return redirect(url_for('main.bet'))
    else:
        return redirect(url_for('main.bet'))

@main.route('/ligi_druzyny', methods=['POST'])
@login_required
def ligi_druzyny():
    check = request.form.get('check')
    liga = int(request.form.get('id_ligi'))
    druzyna = int(request.form.get('id_druzyny'))
    if check == "usun":
        db.session.execute('''DELETE FROM ligi_druzyny WHERE id_ligi = :x AND id_druzyny = :y;''', {"x":liga, "y":druzyna} )
        db.session.commit()
    elif check == "dodaj":
        statement = db.session.execute('''SELECT d.id_druzyny, l.id_ligi FROM druzyny d
                INNER JOIN ligi_druzyny ld ON d.id_druzyny=ld.id_druzyny
                INNER JOIN ligi l ON l.id_ligi = ld.id_ligi
                WHERE d.id_druzyny = :x;''',{"x":druzyna} )
        ld = [ld for ld in statement]
        for row in ld:
            if row.id_ligi == liga:
                flash('Zespół należy już do tej ligi')
                return redirect(url_for('main.bet'))
        
        db.session.execute('''INSERT INTO ligi_druzyny VALUES(:x,:y)''', {"x":liga, "y":druzyna})
        db.session.commit()
    return redirect(url_for('main.bet'))

@main.route('/transakcja', methods=['POST'])
@login_required
def transakcja():
    check = request.form.get('check')
    if check == 'usun':
        id_transakcji = request.form.get('id_transakcji')
        db.session.execute('''DELETE FROM transakcje WHERE id_transakcji = :x;''', {"x":id_transakcji} )
        db.session.commit()
        return redirect(url_for('main.bet'))
    else:
        return redirect(url_for('main.bet'))