import os
import datetime
import jwt
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SECRET = os.environ["JWT_SECRET"]
JWT_EXP_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", "8"))

# ---------------------------------------------------------------
# Connexions à la base : une pour écrire, une pour lire
# ---------------------------------------------------------------
def get_conn(write: bool):
    """Retourne une connexion psycopg2 vers le primaire (write=True)
    ou vers la réplique (write=False), via HAProxy."""
    if write:
        host = os.environ["DB_WRITE_HOST"]
        port = os.environ["DB_WRITE_PORT"]
    else:
        host = os.environ["DB_READ_HOST"]
        port = os.environ["DB_READ_PORT"]
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        cursor_factory=psycopg2.extras.RealDictCursor,
        connect_timeout=5,
    )

# ---------------------------------------------------------------
# Authentification JWT (sessions sans état)
# ---------------------------------------------------------------
def creer_token(user_id: int, matricule: str) -> str:
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "sub": str(user_id),          # <-- chaîne obligatoire
        "matricule": matricule,
        "iat": now,
        "exp": now + datetime.timedelta(hours=JWT_EXP_HOURS),
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def token_requis(f):
    """Décorateur : exige un header Authorization: Bearer <token> valide."""
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"erreur": "token manquant"}), 401
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"erreur": "token expiré"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erreur": "token invalide"}), 401
        request.user = payload
        return f(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------------
# Santé (pour HAProxy option httpchk GET /health)
# ---------------------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------
# Connexion : délivre un JWT
# ---------------------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email:
        return jsonify({"erreur": "email requis"}), 400

    conn = get_conn(write=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, matricule FROM etudiants WHERE email = %s",
                (email,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return jsonify({"erreur": "étudiant inconnu"}), 404

    token = creer_token(row["id"], row["matricule"])
    return jsonify({"token": token, "matricule": row["matricule"]})


# ---------------------------------------------------------------
# ÉCRITURE : créer un étudiant (sur le primaire)
# ---------------------------------------------------------------
@app.route("/etudiants", methods=["POST"])
@token_requis
def creer_etudiant():
    data = request.get_json(silent=True) or {}
    nom, prenom, email = data.get("nom"), data.get("prenom"), data.get("email")
    if not (nom and prenom and email):
        return jsonify({"erreur": "nom, prenom, email requis"}), 400

    conn = get_conn(write=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, matricule FROM etudiants WHERE email = %s",
                (email,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    return jsonify({"id": new_id}), 201


# ---------------------------------------------------------------
# ÉCRITURE : ajouter une note (sur le primaire)
# ---------------------------------------------------------------
@app.route("/notes", methods=["POST"])
@token_requis
def ajouter_note():
    """Ajoute une note à une inscription existante."""
    data = request.get_json(silent=True) or {}
    for k in ("inscription_id", "valeur", "session"):
        if data.get(k) is None:
            return jsonify({"erreur": f"{k} requis"}), 400
    if data["session"] not in ("normale", "rattrapage"):
        return jsonify({"erreur": "session doit être 'normale' ou 'rattrapage'"}), 400

    conn = get_conn(write=True)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO notes (inscription_id, valeur, session) "
                "VALUES (%s, %s, %s) RETURNING id",
                (data["inscription_id"], data["valeur"], data["session"]),
            )
            new_id = cur.fetchone()["id"]
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"erreur": "une note existe déjà pour cette session"}), 409
    finally:
        conn.close()

    return jsonify({"id": new_id}), 201


# ---------------------------------------------------------------
# LECTURE : consulter les notes d'un étudiant (sur la réplique)
# ---------------------------------------------------------------
@app.route("/notes/<int:etudiant_id>", methods=["GET"])
@token_requis
def lire_notes(etudiant_id):
    """Retourne toutes les notes d'un étudiant avec matière et filière."""
    conn = get_conn(write=False)  # lecture sur la réplique
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT n.id, f.libelle AS filiere, m.libelle AS matiere,
                       m.code AS code_matiere, i.annee, n.valeur, n.session,
                       n.saisie_le
                FROM notes n
                JOIN inscriptions i ON n.inscription_id = i.id
                JOIN matieres m ON i.matiere_id = m.id
                JOIN filieres f ON m.filiere_id = f.id
                WHERE i.etudiant_id = %s
                ORDER BY i.annee DESC, m.code, n.session
            """, (etudiant_id,))
            rows = cur.fetchall()
    finally:
        conn.close()

    return jsonify(rows)


# ---------------------------------------------------------------
# Lancement
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)