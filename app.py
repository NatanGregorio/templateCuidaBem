from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask import jsonify
from models import db, Usuario, Meta, RegistroIMC
from datetime import datetime

app = Flask(__name__)

# Configuração do MySQL (ajuste seu usuário e senha)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/imc_check'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"
app.config["SESSION_COOKIE_HTTPONLY"] = True

# Configuração da estrutura do Flask para renderizar páginas
app = Flask(
    __name__,
   
)


# Configuração com o banco de dados
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:root@localhost:3306/agendalab?charset=utf8mb4'
)
db = SQLAlchemy(app)

#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -----------------------
# TABELA DE USUÁRIOS
# -----------------------
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    login = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    altura = db.Column(db.Numeric(5, 2))
    peso = db.Column(db.Numeric(5, 2))
    data_nascimento = db.Column(db.Date)
    sexo = db.Column(db.Enum('Masculino', 'Feminino', 'Outro'))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    metas = db.relationship('Meta', back_populates='usuario', cascade='all, delete')
    registros_imc = db.relationship('RegistroIMC', back_populates='usuario', cascade='all, delete')

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# -----------------------
# TABELA DE METAS
# -----------------------
class Meta(db.Model):
    __tablename__ = 'metas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    peso_desejado = db.Column(db.Numeric(5, 2), nullable=False)
    data_meta = db.Column(db.Date, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', back_populates='metas')

    def __repr__(self):
        return f'<Meta Usuario={self.usuario_id} PesoDesejado={self.peso_desejado}>'

# -----------------------
# TABELA DE REGISTROS DE IMC
# -----------------------
class RegistroIMC(db.Model):
    __tablename__ = 'registros_imc'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    peso_atual = db.Column(db.Numeric(5, 2), nullable=False)
    altura = db.Column(db.Numeric(5, 2), nullable=False)
    imc = db.Column(db.Numeric(5, 2))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', back_populates='registros_imc')

    def calcular_imc(self):
        """Calcula o IMC com base no peso e altura"""
        if self.altura and self.peso_atual:
            self.imc = round(float(self.peso_atual) / (float(self.altura) * float(self.altura)), 2)

    def __repr__(self):
        return f'<RegistroIMC Usuario={self.usuario_id} IMC={self.imc}>'

# Constantes para os templates (mantidas para compatibilidade visual)
ACTIVITY_CATEGORIES = [
    ("caminhada", "Caminhada"),
    ("natacao", "Natação"),
    ("ciclismo", "Ciclismo"),
    ("musculacao", "Musculação"),
    ("pilates", "Pilates"),
]
CATEGORY_LABELS = dict(ACTIVITY_CATEGORIES)

DIABETES_TYPES = [
    ("tipo_1", "Tipo 1"),
    ("tipo_2", "Tipo 2"),
    ("pre_diabetes", "Pré-diabetes"),
    ("gestacional", "Gestacional"),
]
DIABETES_TYPE_LABELS = dict(DIABETES_TYPES)

EMERGENCY_RELATIONS = [
    ("pai", "Pai"),
    ("mae", "Mãe"),
    ("cuidador", "Cuidador"),
]
EMERGENCY_RELATION_LABELS = dict(EMERGENCY_RELATIONS)

ALERT_TYPES = [
    ("medicacao", "Medicação"),
    ("refeicao", "Refeição"),
    ("glicemia", "Medição de Glicemia"),
    ("exercicio", "Exercício físico"),
    ("consulta", "Consulta médica"),
]
ALERT_TYPE_LABELS = dict(ALERT_TYPES)

DAYS_OF_WEEK = [
    ("mon", "Segunda"),
    ("tue", "Terça"),
    ("wed", "Quarta"),
    ("thu", "Quinta"),
    ("fri", "Sexta"),
    ("sat", "Sábado"),
    ("sun", "Domingo"),
]
DAY_LABELS = dict(DAYS_OF_WEEK)

MEASUREMENT_CONTEXTS = [
    ("em_jejum", "Em Jejum"),
    ("antes_refeicao", "Antes da Refeição"),
    ("2h_pos_refeicao", "2h após a refeição"),
    ("antes_dormir", "Antes de dormir"),
]
MEASUREMENT_CONTEXT_LABELS = dict(MEASUREMENT_CONTEXTS)

# Dados mockados para demonstração visual
MOCK_USERS = [
    {
        "id": 1,
        "name": "João Silva",
        "email": "joao@email.com",
        "username": "joao",
        "diabetes_type": "tipo_2",
        "phone": "11987654321",
        "emergency_contact_name": "Maria Silva",
        "emergency_contact_phone": "11987654322",
        "emergency_contact_relation": "mae",
        "active": 1,
        "height": 1.75,
        "weight": 80.0
    },
    {
        "id": 2,
        "name": "Ana Santos",
        "email": "ana@email.com",
        "username": "ana",
        "diabetes_type": "tipo_1",
        "phone": "11987654323",
        "emergency_contact_name": "Pedro Santos",
        "emergency_contact_phone": "11987654324",
        "emergency_contact_relation": "pai",
        "active": 1,
        "height": 1.65,
        "weight": 65.0
    }
]

MOCK_MEASUREMENTS = [
    {"measured_at": "2024-01-15 08:00", "glucose_level": 95, "measurement_context": "em_jejum", "notes": "Medição matinal"},
    {"measured_at": "2024-01-15 12:00", "glucose_level": 140, "measurement_context": "2h_pos_refeicao", "notes": "Após almoço"},
    {"measured_at": "2024-01-14 08:00", "glucose_level": 88, "measurement_context": "em_jejum", "notes": ""},
    {"measured_at": "2024-01-14 19:00", "glucose_level": 120, "measurement_context": "antes_refeicao", "notes": "Antes do jantar"},
]

MOCK_ACTIVITIES = [
    {"category": "caminhada", "performed_at": "2024-01-15 07:00", "duration_minutes": 30},
    {"category": "natacao", "performed_at": "2024-01-14 18:00", "duration_minutes": 45},
    {"category": "ciclismo", "performed_at": "2024-01-13 16:00", "duration_minutes": 60},
]

MOCK_ALERTS = [
    {"id": 1, "alert_type": "medicacao", "alert_time": "08:00", "days": "mon,tue,wed,thu,fri", "alert_date": None},
    {"id": 2, "alert_type": "glicemia", "alert_time": "12:00", "days": "mon,wed,fri", "alert_date": None},
    {"id": 3, "alert_type": "consulta", "alert_time": "14:00", "days": "", "alert_date": "2024-02-15"},
]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Login simplificado - aceita qualquer usuário/senha para demonstração
        if username.lower() == "adm" and password == "adm":
            session.clear()
            session["is_admin"] = True
            session["user_name"] = "Administrador"
            flash("Login de administrador realizado com sucesso!", "success")
            return redirect(url_for("usuarios"))
        elif username and password:
            session["user_id"] = 1
            session["user_name"] = "Usuário Demo"
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("features"))
        else:
            flash("Informe usuário e senha.", "error")

    return render_template("login.html")

@app.route("/esqueci_senha", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if username:
            session["reset_login"] = username
            flash("Login localizado. Informe a nova senha.", "info")
            return redirect(url_for("reset_password"))
        else:
            flash("Informe o login.", "error")

    return render_template("forgot_password.html")



@app.route("/redefinir_senha", methods=["GET", "POST"])
def reset_password():
    username = session.get("reset_login")
    if not username:
        flash("Fluxo de redefinição inválido. Informe seu login.", "error")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if new_password and new_password == confirm_password:
            session.pop("reset_login", None)
            flash("Senha redefinida com sucesso. Faça login.", "success")
            return redirect(url_for("index"))
        else:
            flash("As senhas não coincidem ou estão vazias.", "error")

    return render_template("reset_password.html", username=username)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Simula cadastro bem-sucedido
        flash("Cadastro realizado! Você já pode fazer login.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Faça login para acessar.", "error")
        return redirect(url_for("index"))

    # Dados mockados para o dashboard
    month_key = request.args.get("month") or datetime.now().strftime("%Y-%m")
    
    # Dados simulados para os gráficos
    labels = [m["measured_at"] for m in MOCK_MEASUREMENTS]
    values = [m["glucose_level"] for m in MOCK_MEASUREMENTS]
    
    return render_template(
        "dashboard.html",
        name=session.get("user_name"),
        labels=labels,
        values=values,
        latest_value=values[-1] if values else 100,
        count=len(values),
        avg_7d=110.5,
        min_val=88,
        max_val=140,
        month_key=month_key,
        month_avg=115.2,
        month_min=88,
        month_max=140,
        daily_labels=["2024-01-13", "2024-01-14", "2024-01-15"],
        daily_avgs=[105, 104, 117],
        context_labels=["Em Jejum", "Antes da Refeição", "2h após a refeição"],
        context_avgs=[91, 120, 140],
    )

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("index"))

@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if not session.get("is_admin"):
        flash("Acesso restrito. Faça login como administrador.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        # Simula ações de administração
        action = request.form.get("action")
        if action in ["delete", "activate", "deactivate", "toggle"]:
            flash(f"Ação '{action}' executada com sucesso.", "success")

    return render_template(
        "users.html",
        users=MOCK_USERS,
        diabetes_labels=DIABETES_TYPE_LABELS,
        relation_labels=EMERGENCY_RELATION_LABELS,
    )

@app.route("/account", methods=["GET", "POST"])
def account():
    if "user_id" not in session:
        flash("Faça login para acessar.", "error")
        return redirect(url_for("index"))

    # Usuário mockado
    user = MOCK_USERS[0]

    if request.method == "POST":
        flash("Dados atualizados com sucesso.", "success")
        return redirect(url_for("account"))

    return render_template("account.html", user=user)

@app.route("/features")
def features():
    is_logged_in = "user_id" in session
    return render_template("features.html", is_logged_in=is_logged_in, name=session.get("user_name"))

@app.route("/alerts", methods=["GET", "POST"])
def alerts():
    if "user_id" not in session:
        flash("Faça login para acessar.", "error")
        return redirect(url_for("index"))

    edit_id = request.args.get("edit")
    
    if request.method == "POST":
        action = request.form.get("action")
        if action in ["create", "update"]:
            flash("Alerta salvo com sucesso.", "success")
            return redirect(url_for("alerts"))

    edit_alert = None
    edit_days = []
    if edit_id:
        # Simula busca do alerta para edição
        edit_alert = MOCK_ALERTS[0] if edit_id == "1" else None
        if edit_alert:
            edit_days = edit_alert["days"].split(",") if edit_alert["days"] else []

    return render_template(
        "alerts.html",
        alert_types=ALERT_TYPES,
        days_of_week=DAYS_OF_WEEK,
        alerts=MOCK_ALERTS,
        edit_alert=edit_alert,
        edit_days=edit_days,
        edit_date=edit_alert["alert_date"] if edit_alert else None,
        alert_type_labels=ALERT_TYPE_LABELS,
        day_labels=DAY_LABELS,
        alert_time_default="",
    )

@app.route("/alerts/delete/<int:alert_id>", methods=["POST"])
def delete_alert(alert_id):
    if "user_id" not in session:
        flash("Faça login para acessar.", "error")
        return redirect(url_for("index"))
    
    flash("Alerta excluído.", "success")
    return redirect(url_for("alerts"))

@app.route("/alerts/data")
def alerts_data():
    if "user_id" not in session:
        return {"alerts": []}, 401
    
    def row_to_obj(r):
        days_list = r["days"].split(",") if r["days"] else []
        return {
            "id": r["id"],
            "alert_type": r["alert_type"],
            "alert_type_label": ALERT_TYPE_LABELS.get(r["alert_type"], r["alert_type"]),
            "alert_time": r["alert_time"],
            "days": days_list,
            "alert_date": r["alert_date"],
        }
    return {"alerts": [row_to_obj(r) for r in MOCK_ALERTS]}

@app.route("/measurements", methods=["GET", "POST"])
def measurements():
    if "user_id" not in session:
        flash("Faça login para acessar.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        flash("Medição registrada com sucesso.", "success")
        return redirect(url_for("measurements"))

    now = datetime.now()
    return render_template(
        "measurements.html",
        measurement_contexts=MEASUREMENT_CONTEXTS,
        entries=MOCK_MEASUREMENTS,
        date_default=now.strftime("%Y-%m-%d"),
        time_default="",
    )

@app.route("/activities", methods=["GET", "POST"])
def activities():
    if "user_id" not in session:
        flash("Faça login para acessar.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        flash("Atividade registrada com sucesso.", "success")
        return redirect(url_for("activities"))

    # Dados mockados para o resumo mensal
    month_key = datetime.now().strftime("%Y-%m")
    summary = [
        {"category": "caminhada", "count": 5, "total": 150},
        {"category": "natacao", "count": 3, "total": 135},
        {"category": "ciclismo", "count": 2, "total": 120},
    ]

    now = datetime.now()
    return render_template(
        "activities.html",
        categories=ACTIVITY_CATEGORIES,
        entries=MOCK_ACTIVITIES,
        summary=summary,
        date_default=now.strftime("%Y-%m-%d"),
        time_default="",
        month_key=month_key,
        category_labels=CATEGORY_LABELS,
    )

@app.route("/activities_dashboard")
def activities_dashboard():
    if "user_id" not in session:
        flash("Faça login para acessar.", "error")
        return redirect(url_for("index"))

    month_key = request.args.get("month") or datetime.now().strftime("%Y-%m")

    # Dados mockados para o dashboard de atividades
    category_labels_order = [label for slug, label in ACTIVITY_CATEGORIES]
    counts_per_category = [5, 3, 2, 1, 0]  # caminhada, natacao, ciclismo, musculacao, pilates
    durations_per_category = [150, 135, 120, 30, 0]

    total_activities = sum(counts_per_category)
    total_minutes = sum(durations_per_category)
    top_category_label = "Caminhada"

    labels_days = ["2024-01-13", "2024-01-14", "2024-01-15"]
    durations_daily = [60, 45, 30]

    return render_template(
        "activities_dashboard.html",
        name=session.get("user_name"),
        month_key=month_key,
        category_labels=category_labels_order,
        counts_per_category=counts_per_category,
        durations_per_category=durations_per_category,
        labels_days=labels_days,
        durations_daily=durations_daily,
        total_activities=total_activities,
        total_minutes=total_minutes,
        top_category_label=top_category_label,
    )

@app.route("/admin/db", methods=["GET", "POST"])
def admin_db():
    if not session.get("is_admin"):
        flash("Acesso restrito ao administrador.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        flash("Funcionalidade de banco de dados desabilitada no protótipo.", "info")

    return render_template("admin_db.html", db_path="Protótipo - sem banco de dados")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



# Criação das tabelas
with app.app_context():
    db.create_all()


# -----------------------
# ROTAS USUÁRIO
# -----------------------
@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    data = request.json
    usuario = Usuario(
        nome=data['nome'],
        email=data['email'],
        telefone=data.get('telefone'),
        login=data['login'],
        senha=data['senha'],
        altura=data.get('altura'),
        peso=data.get('peso'),
        data_nascimento=datetime.strptime(data['data_nascimento'], '%Y-%m-%d'),
        sexo=data.get('sexo')
    )
    db.session.add(usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário criado com sucesso!'}), 201


@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([{
        'id': u.id,
        'nome': u.nome,
        'email': u.email,
        'sexo': u.sexo,
        'data_cadastro': u.data_cadastro
    } for u in usuarios])


# -----------------------
# ROTAS META
# -----------------------
@app.route('/metas', methods=['POST'])
def criar_meta():
    data = request.json
    meta = Meta(
        usuario_id=data['usuario_id'],
        peso_desejado=data['peso_desejado'],
        data_meta=datetime.strptime(data['data_meta'], '%Y-%m-%d')
    )
    db.session.add(meta)
    db.session.commit()
    return jsonify({'mensagem': 'Meta criada com sucesso!'}), 201


@app.route('/metas/<int:usuario_id>', methods=['GET'])
def listar_metas_usuario(usuario_id):
    metas = Meta.query.filter_by(usuario_id=usuario_id).all()
    return jsonify([{
        'id': m.id,
        'peso_desejado': str(m.peso_desejado),
        'data_meta': m.data_meta.strftime('%Y-%m-%d')
    } for m in metas])


# -----------------------
# ROTAS REGISTRO DE IMC
# -----------------------
@app.route('/imc', methods=['POST'])
def registrar_imc():
    data = request.json
    registro = RegistroIMC(
        usuario_id=data['usuario_id'],
        peso_atual=data['peso_atual'],
        altura=data['altura']
    )
    registro.calcular_imc()
    db.session.add(registro)
    db.session.commit()
    return jsonify({
        'mensagem': 'Registro de IMC criado com sucesso!',
        'imc': float(registro.imc)
    }), 201


@app.route('/imc/<int:usuario_id>', methods=['GET'])
def listar_registros_imc(usuario_id):
    registros = RegistroIMC.query.filter_by(usuario_id=usuario_id).all()
    return jsonify([{
        'id': r.id,
        'peso_atual': float(r.peso_atual),
        'altura': float(r.altura),
        'imc': float(r.imc),
        'data_registro': r.data_registro.strftime('%Y-%m-%d %H:%M')
    } for r in registros])


if __name__ == '__main__':
    app.run(debug=True)
