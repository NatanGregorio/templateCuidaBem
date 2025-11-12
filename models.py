from flask_sqlalchemy import SQLAlchemy
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
