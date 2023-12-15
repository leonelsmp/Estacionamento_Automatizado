from flask import Flask, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
from flask_socketio import SocketIO, emit, Namespace
import os
from datetime import datetime ,timezone, timedelta
from flask_cors import CORS
#https://southcarpark.netlify.app/

# Init app
# Create a custom namespace
class MyNamespace(Namespace):
    def on_connect(self):
        print('Client connected')

    def on_disconnect(self):
        print('Client disconnected')

app = Flask(__name__)
socketIO = SocketIO(app, cors_allowed_origins="*", namespace='/mynamespace')
socketIO.on_namespace(MyNamespace('/mynamespace'))
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

#===================================================================================================
# Classe Historico
class Historico(db.Model):
    Hid = db.Column(db.Integer, primary_key=True)
    Vagaid = db.Column(db.Integer, nullable=False)
    DataInicio = db.Column(db.DateTime, nullable=False)
    DataFim = db.Column(db.DateTime, nullable=True)

    def __init__(self, Vagaid, DataInicio, DataFim):
        self.Vagaid = Vagaid
        self.DataInicio = DataInicio
        self.DataFim = DataFim


# schema Historico
class HistoricoSchema(ma.Schema):
  class Meta:
    fields = ('Hid', 'Vagaid', 'DataInicio', 'DataFim')

# Init schema
Historico_schema = HistoricoSchema()
Historicos_schema = HistoricoSchema(many=True)
#===================================================================================================
#===================================================================================================
# Classe Vagas
class Vagas(db.Model):
    Vagaid = db.Column(db.Integer, primary_key = True, autoincrement=False)
    Ocupada = db.Column(db.Boolean, nullable=False)

    def __init__(self, Vagaid, Ocupada):
        self.Vagaid = Vagaid
        self.Ocupada = Ocupada

# schema Vagas
class VagasSchema(ma.Schema):
  class Meta:
    fields = ('Vagaid', 'Ocupada')

# Init schema
Vaga_schema = VagasSchema()
Vagas_schema = VagasSchema(many=True)
#===================================================================================================

@app.route('/')
def Home():
    return "Bem vindo ao estacionamento", 200

# Carro entrou na vaga
@app.route('/Entrou', methods=['POST'])
def entrou_carro():
    Vagaid = request.json['Vagaid']
    utc_offset = timedelta(hours=-3)
    utc_time = datetime.now(timezone.utc)
    DataInicio = utc_time + utc_offset
    DataFim = None
    vaga = Vagas.query.get(Vagaid)
    if(vaga.Ocupada == True):
        return "Vaga ocupada", 200
    else:
        carro = Historico(Vagaid, DataInicio, DataFim)
        vaga.Ocupada = True
        db.session.add(carro)
        db.session.add(vaga)
        db.session.commit()
        try:
          emit('message', json.loads(Vaga_schema.jsonify(vaga).data), namespace='/mynamespace', broadcast=True)
        except Exception as e:
          pass
        return Historico_schema.jsonify(carro), 200

# Carro saiu da vaga
@app.route('/Saiu', methods=['POST'])
def saiu_carro():
    Vagaid = request.json['Vagaid']
    carro = Historico.query.filter_by(Vagaid=Vagaid).order_by(Historico.DataInicio.desc()).first()
    vaga = Vagas.query.get(Vagaid)
    if(vaga.Ocupada == True):
        vaga.Ocupada = False
        utc_offset = timedelta(hours=-3)
        utc_time = datetime.now(timezone.utc)
        carro.DataFim = utc_time + utc_offset

        db.session.add(carro)
        db.session.add(vaga)
        db.session.commit()
        try:
          emit('message', json.loads(Vaga_schema.jsonify(vaga).data),namespace='/mynamespace', broadcast=True)
        except Exception as e:
          pass
        return Historico_schema.jsonify(carro)
    else:
        return "Vaga livre", 200

# Pegar todo o historico
@app.route('/Historico', methods=['GET'])
def get_historico():
  tudo = Historico.query.all()
  result = Historicos_schema.dump(tudo)
  return jsonify(result)

# Pegar todas as vagas
@app.route('/Vagas', methods=['GET'])
def get_vagas():
  tudo = Vagas.query.all()
  result = Vagas_schema.dump(tudo)
  return jsonify(result)

# Pegar status de uma vaga
@app.route('/Vagas/<Vagaid>', methods=['GET'])
def get_vaga(Vagaid):
  vaga = Vagas.query.get(Vagaid)
  return Vaga_schema.jsonify(vaga)

# Run Server
if __name__ == '__main__':
  #app.run(debug=True)
  socketIO.run(app, debug=True)