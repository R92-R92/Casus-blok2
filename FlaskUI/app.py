from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash
from Controllers.DatabaseController import DatabaseController
from Controllers.PlanningController import PlanningController
from auth import login_required

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Nodig voor sessiebeheer

db = DatabaseController()


def get_user_by_email(email):
    db = DatabaseController()  # Open een nieuwe databaseverbinding
    users = db.fetch_by_condition("Gebruiker", {"Email": email})
    return users[0] if users else None


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)

        if user and user[5] == password:  # user[4] is het wachtwoord
            session['user_id'] = user[0]  # user[0] is de ID
            session['role'] = user[4]  # user[5] is de rol_id
            return redirect('/dashboard')

        return "Ongeldige login!", 403

    return render_template('login.html')


@app.route('/dashboard')
@login_required()
def dashboard():
    rol = session['role']  # Haal de rol van de gebruiker uit de sessie
    if rol == 3:  # Beheerder
        return render_template('dashboard_beheerder.html')  # Specifieke template voor beheerder
    elif rol == 2:  # Administrator
        return render_template('dashboard_admin.html')  # Specifieke template voor admin
    elif rol == 1:  # Docent
        return render_template('dashboard_docent.html')  # Specifieke template voor docent
    elif rol == 0:  # Gebruiker
        return render_template('dashboard_gebruiker.html')  # Specifieke template voor gebruiker
    else:  # Geblokkeerd of ongeldige rol
        return redirect('/')


@app.route('/beheerder')
@login_required(role=3)  # Alleen beheerder mag dit zien
def beheerder_panel():
    return render_template('beheerder_panel.html')


@app.route('/admin')
@login_required(role=2)  # Alleen admin mag dit zien
def admin_panel():
    return render_template('admin_panel.html')


@app.route('/docent')
@login_required(role=1)  # Alleen docent en hoger mogen dit zien
def docent_panel():
    return render_template('docent_panel.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


def get_all_users():
    return db.fetch_all("Gebruiker")


def get_user_by_id(user_id):
    users = db.fetch_by_condition("Gebruiker", {"id": user_id})
    return users[0] if users else None


@app.route('/gebruikers')
@login_required(role=2)  # Alleen admin en beheerder mogen dit zien
def gebruikers_overzicht():
    gebruikers = get_all_users()  # Dit haalt alle gebruikers op uit de database
    return render_template('gebruikers.html', gebruikers=gebruikers)


@app.route('/gebruikers/toevoegen', methods=['GET', 'POST'])
@login_required(role=2)
def gebruikers_toevoegen():
    if request.method == 'POST':
        voornaam = request.form['voornaam']
        achternaam = request.form['achternaam']
        email = request.form['email']
        rol = int(request.form['rol'])

        # Controleer of de beheerder geen hogere rol kan aanmaken dan hijzelf
        if session['role'] == 2 and rol >= 2:
            return "Geen toestemming om deze rol aan te maken!", 403

        # Standaard wachtwoord instellen, kan verder worden aangepast
        wachtwoord = request.form['wachtwoord'] if 'wachtwoord' in request.form else 'default'

        # Voeg gebruiker toe via databasecontroller
        db.insert("Gebruiker", {
            "Voornaam": voornaam,
            "Achternaam": achternaam,
            "Email": email,
            "Rol_id": rol,
            "Wachtwoord": wachtwoord
        })

        # Redirect naar gebruikersoverzicht
        return redirect('/gebruikers')

    return render_template('gebruiker_toevoegen.html')


@app.route('/gebruikers/verwijderen/<int:id>')
@login_required(role=2)  # Alleen admin en beheerder mogen dit doen
def gebruikers_verwijderen(id):
    gebruiker = get_user_by_id(id)
    if not gebruiker:
        return "Gebruiker niet gevonden", 404

    if session['role'] == 2 and gebruiker[5] >= 2:
        return "Geen toestemming om deze gebruiker te verwijderen!", 403

    db.delete("Gebruiker", {"id": id})
    return redirect('/gebruikers')


@app.route('/gebruikers/blokkeren/<int:id>')
@login_required(role=2)  # Alleen admin en beheerder mogen dit doen
def gebruikers_blokkeren(id):
    gebruiker = get_user_by_id(id)
    if not gebruiker:
        return "Gebruiker niet gevonden", 404

    if session['role'] == 2 and gebruiker[5] >= 2:
        return "Geen toestemming om deze gebruiker te blokkeren!", 403

    db.update("Gebruiker", {"Rol_id": -1}, {"id": id})
    return redirect('/gebruikers')


planning_controller = PlanningController()


@app.route('/planning')
@login_required()
def planning_overzicht():
    reserveringen = planning_controller.get_all_reservations()
    return render_template('planning.html', reserveringen=reserveringen)


@app.route('/planning/toevoegen', methods=['GET', 'POST'])
@login_required(role=1)  # Alleen docenten en hoger mogen reserveringen maken
def planning_toevoegen():
    if request.method == 'POST':
        datum = request.form['datum']
        tijd = request.form['tijd']
        beschrijving = request.form['beschrijving']
        gebruiker_id = session['user_id']  # De ingelogde gebruiker

        planning_controller.create_reservation(gebruiker_id, datum, tijd, beschrijving)
        return redirect('/planning')

    return render_template('planning_toevoegen.html')


@app.route('/planning/wijzigen/<int:id>', methods=['GET', 'POST'])
@login_required(role=2)  # Alleen admins en beheerders mogen reserveringen wijzigen
def planning_wijzigen(id):
    reservering = planning_controller.get_reservation_by_id(id)
    if not reservering:
        return "Reservering niet gevonden", 404

    if request.method == 'POST':
        datum = request.form['datum']
        tijd = request.form['tijd']
        beschrijving = request.form['beschrijving']

        planning_controller.update_reservation(id, datum, tijd, beschrijving)
        return redirect('/planning')

    return render_template('planning_wijzigen.html', reservering=reservering[0])


@app.route('/planning/verwijderen/<int:id>')
@login_required(role=2)  # Alleen admins en beheerders mogen reserveringen verwijderen
def planning_verwijderen(id):
    reservering = planning_controller.get_reservation_by_id(id)
    if not reservering:
        return "Reservering niet gevonden", 404

    planning_controller.delete_reservation(id)
    return redirect('/planning')


# ------------------------------------------------------------------------------------------------------- #
@app.route('/planning/docent')
@login_required(role=1)  # Alleen docenten en hoger
def planning_docent():
    reserveringen = planning_controller.get_all_reservations()
    return render_template('planning_docent.html', reserveringen=reserveringen)


@app.route('/planning/docent/toevoegen', methods=['GET', 'POST'])
@login_required(role=1)  # Alleen docenten mogen reserveringen maken
def planning_docent_toevoegen():
    if request.method == 'POST':
        datum = request.form['datum']
        tijd = request.form['tijd']
        beschrijving = request.form['beschrijving']
        gebruiker_id = session['user_id']  # De ingelogde docent

        planning_controller.create_reservation(gebruiker_id, datum, tijd, beschrijving)
        return redirect('/planning/docent')

    return render_template('planning_docent_toevoegen.html')


@app.route('/planning/gebruiker')
@login_required(role=0)  # Alleen gebruikers en hoger
def planning_gebruiker():
    reserveringen = planning_controller.get_all_reservations()
    return render_template('planning_gebruiker.html', reserveringen=reserveringen)

