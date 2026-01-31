import uuid
from typing import Annotated, List
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import Depends, FastAPI, HTTPException, Query
from datetime import date, datetime, time
from enum import Enum


class TipoUsuario(str, Enum):
    MEDICO = "medico"
    FUNCIONARIO = "funcionario"
    PACIENTE = "paciente"



# Tabelas da base de dados

class Usuario(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    senha_has: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    tipo_usuario: TipoUsuario = Field(index=True, nullable=False)
    

class Paciente(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nome: str = Field(nullable=False)
    idade: int =  Field(nullable=False)
    genero: str = Field(nullable=False)
    num_bi: str = Field(nullable=False)
    telefone: str = Field(nullable=False)
    endereco: str = Field(nullable=False)
    email: str = Field(unique=True)
    data_registro: datetime =  Field(nullable=False)
    usuario_id: uuid.UUID = Field(foreign_key="usuario.id", nullable=False)



class Medico(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)
    nome_medico: str = Field(nullable=False)
    especialidade: str = Field(nullable=False)
    telefone: str = Field(nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    usuario_id: uuid.UUID = Field(foreign_key="usuario.id", nullable=False)



class Funcionario(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)
    nome_funcionario: str = Field(nullable=False)
    cargo: str = Field(nullable=False)
    telefone: str = Field(nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    usuario_id: uuid.UUID = Field(foreign_key="usuario.id", nullable=False)
     
  


class Marcacao(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)
    data_marcacao: date = Field(nullable=False)
    hora_marcacao: time = Field(index=True, unique=True, nullable=False)
    estado_marcacao: str = Field(nullable=False)
    paciente_id: uuid.UUID = Field(foreign_key="paciente.id", nullable=False)
    medico_id: uuid.UUID = Field(foreign_key="medico.id", nullable=False)
    

class Servico(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)
    nome_servico: str = Field(nullable=False)
    descricao: str = Field(nullable=False)
    preco: float = Field(nullable=False)
   


class Consulta(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)
    data_consulta: date = Field(nullable=False)
    hora_consulta: time = Field(index=True, unique=True, nullable=False)
    marcacao_id: uuid.UUID = Field(foreign_key="marcacao.id", nullable=False)
    paciente_id: uuid.UUID = Field(foreign_key="paciente.id", nullable=False)
    medico_id: uuid.UUID = Field(foreign_key="medico.id", nullable=False)
    servico_id: uuid.UUID = Field(foreign_key="servico.id", nullable=False)



class ConsultaService(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)
    consulta_id: uuid.UUID = Field(foreign_key="consulta.id", nullable=False)
    servico_id: uuid.UUID = Field(foreign_key="servico.id", nullable=False)
    quantidade: int = Field(nullable=False)


   
class Pagamento(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)
    valor_pagamento: float = Field(nullable=False)
    metodo_pagamento: str = Field(nullable=False)
    data_pagamento: date = Field(nullable=False)
    estado_pagamento: str = Field(nullable=False)
    paciente_id: uuid.UUID = Field(foreign_key="paciente.id", nullable=False)
    consulta_id: uuid.UUID = Field(foreign_key="consulta.id", nullable=False)
    

db_file = "database.db"
url = f"sqlite:///{db_file}"

engine = create_engine(url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session: 
        yield session
        
DBSession = Annotated[Session, Depends(get_session)]
app = FastAPI( title="Sistema de Gestão de Clínica (de pequena escala)")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

#### USUÁRIOS APIENDPOINTS ###

@app.post("/usuarios", response_model=Usuario)
def criar_usuario(usuario: Usuario):
    with Session(engine) as session:
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario


@app.get("/usuarios", response_model=List[Usuario])
def listar_usuarios():
    with Session(engine) as session:
        return session.exec(select(Usuario)).all()


@app.get("/usuarios/{usuario_id}", response_model=Usuario)
def buscar_usuario(usuario_id: uuid.UUID):
    with Session(engine) as session:
        usuario = session.get(Usuario, usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario


@app.put("/usuarios/{usuario_id}", response_model=Usuario)
def atualizar_usuario(usuario_id: uuid.UUID, dados: Usuario):
    with Session(engine) as session:
        usuario = session.get(Usuario, usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        usuario.nome = dados.nome
        usuario.senha = dados.senha
        usuario.email = dados.email

        usuario. tipo_usuario= dados.tipo_usuario
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario


@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: uuid.UUID):
    with Session(engine) as session:
        usuario = session.get(Usuario, usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        session.delete(usuario)
        session.commit()
        return {"mensagem": "Usuário eliminado com sucesso"}



#### PACIENTES API ENDPOINTS ####

@app.post("/pacientes", response_model=Paciente)
def criar_paciente(paciente: Paciente):
    with Session(engine) as session:
        session.add(paciente)
        session.commit()
        session.refresh(paciente)
        return paciente


@app.get("/pacientes", response_model=List[Paciente])
def listar_pacientes():
    with Session(engine) as session:
        return session.exec(select(Paciente)).all()


@app.get("/pacientes/{paciente_id}", response_model=Paciente)
def buscar_paciente(paciente_id: uuid.UUID):
    with Session(engine) as session:
        paciente = session.get(Paciente, paciente_id)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        return paciente


@app.put("/pacientes/{paciente_id}", response_model=Paciente)
def atualizar_paciente(paciente_id: uuid.UUID, dados: Paciente):
    with Session(engine) as session:
        paciente = session.get(Paciente, paciente_id)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")

        paciente.nome = dados.nome
        paciente.idade = dados.idade
        paciente.genero = dados.genero
        paciente.num_bi = dados.num_bi
        paciente.telefone = dados.telefone
        paciente.endereco = dados.endereco
        paciente.email = dados.email
        paciente.data_registro = dados.data_registro
        paciente.user_id = dados.user_id

        session.add(paciente )
        session.commit()
        session.refresh(paciente)
        return paciente


@app.delete("/pacientes/{paciente_id}")
def eliminar_paciente(paciente_id: uuid.UUID):
    with Session(engine) as session:
        paciente = session.get(Paciente, paciente_id)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")

        session.delete(paciente)
        session.commit()
        return {"mensagem": "Paciente eliminado com sucesso"}



#### MÉDICOS API ENDPOINTS ####

@app.post("/medicos", response_model=Medico)
def criar_medico(medico: Medico):
    with Session(engine) as session:
        session.add(medico)
        session.commit()
        session.refresh(medico)
        return medico


@app.get("/medicos", response_model=List[Medico])
def listar_medicos():
    with Session(engine) as session:
        return session.exec(select(Medico)).all()


@app.get("/medicos/{medico_id}", response_model=Medico)
def buscar_medico(medico_id: uuid.UUID):
    with Session(engine) as session:
        medico = session.get(Medico, medico_id)
        if not medico:
            raise HTTPException(status_code=404, detail="Médico não encontrado")
        return medico


@app.put("/medicos/{medico_id}", response_model=Medico)
def atualizar_medico(medico_id: uuid.UUID, dados: Medico):
    with Session(engine) as session:
        medico = session.get(Medico, medico_id)
        if not medico:
            raise HTTPException(status_code=404, detail="Médico não encontrado")

        medico.nome = dados.nome
        medico.especialidade = dados.especialidade
        medico.telefone = dados.telefone
        medico.user_id = dados.user_id
        session.add(medico)
        session.commit()
        session.refresh(medico)
        return medico


@app.delete("/medicos/{medico_id}")
def eliminar_medico(medico_id: uuid.UUID):
    with Session(engine) as session:
        medico = session.get(Medico, medico_id)
        if not medico:
            raise HTTPException(status_code=404, detail="Médico não encontrado")

        session.delete(medico)
        session.commit()
        return {"mensagem": "Médico eliminado com sucesso"}



#### FUNCIONARIOS API ENDPOINTS ####

@app.post("/funcionario", response_model=Medico)
def criar_funcionario(funcionario: Funcionario):
    with Session(engine) as session:
        session.add(funcionario)
        session.commit()
        session.refresh(funcionario)
        return funcionario


@app.get("/funcionario", response_model=List[Funcionario])
def listar_funcionario():
    with Session(engine) as session:
        return session.exec(select(Funcionario)).all()


@app.get("/funcionarios/{funcionario_id}", response_model=Funcionario)
def buscar_funcionario(funcionario_id: uuid.UUID):
    with Session(engine) as session:
        func = session.get(Funcionario, funcionario_id)
        if not func:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        return func


@app.put("/funcionarios/{funcionario_id}", response_model=Funcionario)
def atualizar_funcionario(funcionario_id: uuid.UUID, dados: Funcionario):
    with Session(engine) as session:
        funcionario = session.get(Funcionario, funcionario_id)
        if not funcionario:
            raise HTTPException(status_code=404, detail="Funcionario não encontrado")

        funcionario.nome = dados.nome
        funcionario.cargo = dados.cargo
        funcionario.telefone = dados.telefone
        funcionario.email = dados.email
        funcionario.user_id = dados.user_id

        session.add(funcionario)
        session.commit()
        session.refresh(funcionario)
        return funcionario

@app.delete("/funcionarios/{funcionario_id}")
def eliminar_funcionario(funcionario_id: uuid.UUID):
    with Session(engine) as session:
        funcionario = session.get(Funcionario, funcionario_id)
        if not funcionario:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")

        session.delete(funcionario)
        session.commit()
        return {"mensagem": "Funcionario eliminado com sucesso"}


    #### MARCAÇÃO API ENDPOINTS ####

@app.post("/marcacao", response_model=Marcacao)
def criar_marcacao(marcacao: Marcacao):
    with Session(engine) as session:
        session.add(marcacao)
        session.commit()
        session.refresh(marcacao)
        return marcacao


@app.get("/marcacao", response_model=List[Marcacao])
def listar_marcacao():
    with Session(engine) as session:
        return session.exec(select(Marcacao)).all()


@app.get("/marcacao/{marcacao_id}", response_model=Marcacao)
def buscar_marcacao(marcacao_id: uuid.UUID):
    with Session(engine) as session:
        marcacao = session.get(Marcacao, marcacao_id)
        if not marcacao:
            raise HTTPException(status_code=404, detail="Marcação não encontrado")
        return marcacao


@app.put("/marcacao/{marcacao_id}", response_model=Marcacao)
def atualizar_marcacao(marcacao_id: uuid.UUID, dados: Marcacao):
    with Session(engine) as session:
        marcacao = session.get(Marcacao, marcacao_id)
        if not marcacao:
            raise HTTPException(status_code=404, detail="Marcação não encontrado")

        marcacao.data_marcacao = dados.data_marcacao
        marcacao.hora_marcacao = dados.hora_marcacao 
        marcacao.estado_marcacao = dados.estado_marcacao
        marcacao.paciente_id = dados.paciente_id
        marcacao.medico_id = dados.medico_id
        
        session.add(marcacao)
        session.commit()
        session.refresh(marcacao)
        return marcacao


@app.delete("/marcacao/{marcacao_id}")
def eliminar_marcacao(marcacao_id: uuid.UUID):
    with Session(engine) as session:
        marcacao = session.get(Marcacao, marcacao_id)
        if not marcacao:
            raise HTTPException(status_code=404, detail="Marcação não encontrado")

        session.delete(marcacao)
        session.commit()
        return {"mensagem": "Marcação eliminado com sucesso"}




#### SERVIÇO API ENDPOINTS ####

@app.post("/servicos", response_model=Servico)
def criar_servico(servico: Servico):
    with Session(engine) as session:
        session.add(servico)
        session.commit()
        session.refresh(servico)
        return servico


@app.get("/servicos", response_model=List[Servico])
def listar_servico():
    with Session(engine) as session:
        return session.exec(select(Servico)).all()


@app.get("/servicos/{servico_id}", response_model=Servico)
def buscar_servico(servico_id: uuid.UUID):
    with Session(engine) as session:
        servico = session.get(Servico, servico_id)
        if not servico:
            raise HTTPException(status_code=404, detail="Serviço não encontrado")
        return servico


@app.put("/servicos/{servico_id}", response_model=Servico)
def atualizar_servico(servico_id: uuid.UUID, dados: Servico):
    with Session(engine) as session:
        servico = session.get(Servico, servico_id)
        if not servico:
            raise HTTPException(status_code=404, detail="Serviço não encontrado")

        servico.nome_servico = dados.nome_servico
        servico.descricao = dados.descricao 
        servico. preco = dados.preco
        
        session.add(servico)
        session.commit()
        session.refresh(servico)
        return servico


@app.delete("/servicos/{servico_id}")
def eliminar_servico(servico_id: uuid.UUID):
    with Session(engine) as session:
        a = session.get(Servico, servico_id)
        if not a:
            raise HTTPException(status_code=404, detail="Serviço não encontrado")

        session.delete(a)
        session.commit()
        return {"mensagem": "Serviço eliminado com sucesso"}



## CONSULTA API ENDPOINTS ##

@app.post("/consultas", response_model=Consulta)
def criar_Consulta(consulta: Consulta):
    with Session(engine) as session:
        session.add(consulta)
        session.commit()
        session.refresh(consulta)
        return consulta


@app.get("/consultas", response_model=List[Consulta])
def listar_consulta():
    with Session(engine) as session:
        return session.exec(select(Consulta)).all()


@app.get("/consultas/{consulta_id}", response_model=Consulta)
def buscar_consulta(consulta_id: uuid.UUID):
    with Session(engine) as session:
        consulta = session.get(Consulta, consulta_id)
        if not consulta:
            raise HTTPException(status_code=404, detail="Consulta não encontrado")
        return consulta


@app.put("/consultas/{consulta_id}", response_model=Consulta)
def atualizar_consulta(consulta_id: uuid.UUID, dados: Consulta):
    with Session(engine) as session:
        consulta = session.get(Consulta, consulta_id)
        if not consulta:
            raise HTTPException(status_code=404, detail="Consulta não encontrado")

        consulta.data_consulta = dados.data_consulta
        consulta.hora_consulta = dados.hora_consulta 
        consulta. marcacao_id = dados.marcacao_id
        consulta. paciente_id = dados.paciente_id
        consulta. medico_id = dados.medico_id
        consulta. servico_id = dados.servico_id

        session.add(consulta)
        session.commit()
        session.refresh(consulta)
        return consulta


@app.delete("/consultas/{consulta_id}")
def eliminar_consulta(consulta_id: uuid.UUID):
    with Session(engine) as session:
        consulta = session.get(Consulta, consulta_id)
        if not consulta:
            raise HTTPException(status_code=404, detail="Consulta não encontrado")

        session.delete(consulta)
        session.commit()
        return {"mensagem": "Consulta eliminado com sucesso"}



        #### CONSULTA_SERVIÇO API ENDPOINT ####


# @app.post("/consulta_servico", response_model=Consulta_Servico)
# def criar_Consulta(consulta_servico: Consulta_Servico):
#     with Session(engine) as session:
#         session.add(consulta_servico)
#         session.commit()
#         session.refresh(consulta_servico)
#         return consulta_servico


# @app.get("/consulta_servico", response_model=List[Consulta_Servico])
# def listar_consulta_servico():
#     with Session(engine) as session:
#         return session.exec(select(Consulta_Servico)).all()


# @app.get("/consulta_serviso/{consulta_servico_id}", response_model=Consulta_Servico)
# def buscar_consulta_servico(consulta_servico_id: uuid.UUID):
#     with Session(engine) as session:
#         consulta_servico = session.get(Consulta_Servico, consulta_servico_id)
#         if not consulta_servico:
#             raise HTTPException(status_code=404, detail="Consulta_servico não encontrado")
#         return consulta_servico


# @app.put("/consulta_servico/{consulta_servico_id}", response_model=Consulta_Servico)
# def atualizar_consulta_servico(consulta_servico_id: uuid.UUID, dados: Consulta_Servico):
#     with Session(engine) as session:
#         consulta_servico = session.get(Consulta_Servico, consulta_servico_id)
#         if not consulta_servico:
#             raise HTTPException(status_code=404, detail="Consulta_Serviço não encontrado")

#         consulta_servico.consulta_id = dados.consulta_id
#         consulta_servico.servico_id = dados.servico_id 
#         consulta_servico. quantidade = dados.quantidade
        
#         session.add(consulta_servico)
#         session.commit()
#         session.refresh(consulta_servico)
#         return consulta_servico


# @app.delete("/consulta_servico/{consulta_servico_id}")
# def eliminar_consulta_servico(consulta_servico_id: uuid.UUID):
#     with Session(engine) as session:
#         consulta_servico = session.get(Consulta_Serviço, consulta_servico_id)
#         if not consulta_servico:
#             raise HTTPException(status_code=404, detail="Consulta_Serviço não encontrado")

#         session.delete(consulta_servico)
#         session.commit()
#         return {"mensagem": "Consulta_Serviço eliminado com sucesso"}



        #### PAGAMENTO API ENDPOINTS ####


@app.post("/pagamentos", response_model=Pagamento)
def criar_pagamento(pagamento: Pagamento):
    with Session(engine) as session:
        session.add(pagamento)
        session.commit()
        session.refresh(pagamento)
        return pagamento


@app.get("/pagamentos", response_model=list[Pagamento])
def listar_pagamento():
    with Session(engine) as session:
        return session.exec(select(Pagamento)).all()


@app.get("/pagamentos/{pagamento_id}", response_model=Pagamento)
def buscar_pagamento(pagamento_id: uuid.UUID):
    with Session(engine) as session:
        pagamento_db = session.get(Pagamento, pagamento_id)
        if not pagamento_db:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        return pagamento_db

@app.put("/pagamentos/{pagamento_id}", response_model=Pagamento)
def atualizar_pagamento(pagamento_id: uuid.UUID, dados: Pagamento):
    with Session(engine) as session:
        pagamento = session.get(Pagamento, pagamento_id)
        if not pagamento:
            raise HTTPException(status_code=404, detail="Pagamentos não encontrado")

        pagamento.valor_pagamento  = dados.valor_pagamento
        pagamento.metodo_pagamento = dados.metodo_pagamento 
        pagamento.data_pagamento = dados.data_pagamento
        pagamento.estado = dados.estado
        pagamento.paciente_id = dados.paciente_id
        pagamento.consulta_id = dados.consulta_id

        session.add(pagamento)
        session.commit()
        session.refresh(pagamento)
        return pagamento


@app.delete("/pagamentos/{pagamento_id}")
def eliminar_pagamento(pagamento_id: uuid.UUID):
    with Session(engine) as session:
        pagamento = session.get(Pagamento, pagamento_id)
        if not pagamento:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")

        session.delete(pagamento)
        session.commit()
        return {"mensagem": "Pagamento eliminado com sucesso"}


# end of file api.py