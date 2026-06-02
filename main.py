from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query

from sqlmodel import select, func
from database import SessionDep, create_db_and_tables
from models import Usuario, UsuarioPublico, CreateUsuario, UpdateUsuario, Veiculo, VeiculoPublico, CreateVeiculo, UpdateVeiculo, Reserva, ReservaPublica, ReservaDetalhada, CreateReserva, UpdateReserva

from security import gerar_hash, verificar_senha

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


#login

@app.post("/login")
def login(email: str, senha: str, session: SessionDep):
    
    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    if not verificar_senha(senha, usuario.senha):
        raise HTTPException(
            status_code=401,
            detail="Senha incorreta."
        )

    return {
        "mensagem": "Login realizado com sucesso!",
        "id": usuario.id,
        "nome": usuario.nome,
        "tipo_usuario": usuario.tipo_usuario
    }

#rotas usuário

@app.post("/usuarios", response_model=UsuarioPublico)
def criar_usuario(usuario: CreateUsuario, session: SessionDep):

    db_usuario = Usuario(
        nome=usuario.nome,
        cpf=usuario.cpf,
        email=usuario.email,
        cnh=usuario.cnh,
        tipo_usuario=usuario.tipo_usuario,
        senha=gerar_hash(usuario.senha)
    )

    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)

    return db_usuario

@app.get("/usuarios", response_model=list[UsuarioPublico])
def listar_usuarios(session: SessionDep):
    return session.exec(select(Usuario)).all()


@app.get("/usuarios/{nome_usuario}", response_model=UsuarioPublico)
def buscar_usuario(nome_usuario: str, session: SessionDep):

    consulta = select(Usuario).where(func.lower(Usuario.nome) == nome_usuario.lower())
    usuario = session.exec(consulta).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return usuario


@app.patch("/usuarios/{id_usuario}", response_model=UsuarioPublico)
def atualizar_usuario(id_usuario: int, dados: UpdateUsuario, session: SessionDep):

    usuario = session.get(Usuario, id_usuario)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    dados_update = dados.model_dump(exclude_unset=True)

    if "senha" in dados_update:
        dados_update["senha"] = gerar_hash(dados_update["senha"])

    usuario.sqlmodel_update(dados_update)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return usuario

@app.delete("/usuarios/{id_usuario}")
def deletar_usuario(id_usuario: int, session: SessionDep):

    usuario = session.get(Usuario, id_usuario)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    session.delete(usuario)
    session.commit()

    return {"mensagem": "Usuário deletado com sucesso."}


#rotas veículo

@app.post("/veiculos", response_model=VeiculoPublico)
def cadastrar_veiculo(veiculo: CreateVeiculo, session: SessionDep):

    db_veiculo = Veiculo.model_validate(veiculo)
    session.add(db_veiculo)
    session.commit()
    session.refresh(db_veiculo)

    return db_veiculo


@app.get("/veiculos", response_model=list[VeiculoPublico])
def listar_veiculos(session: SessionDep):
    return session.exec(select(Veiculo)).all()


@app.get("/veiculos/disponiveis", response_model=list[VeiculoPublico])
def veiculos_disponiveis(data_inicio: str, data_fim: str, session: SessionDep):
    
    # Busca veículos que NÃO têm conflito de reserva no período
    reservados = session.exec(
        select(Reserva.id_veiculo).where(
            Reserva.data_inicio < data_fim,
            Reserva.data_fim > data_inicio,
        )
    ).all()

    disponiveis = session.exec(
        select(Veiculo).where(Veiculo.id.not_in(reservados))
    ).all()

    return disponiveis


@app.get("/veiculos/{id_veiculo}", response_model=VeiculoPublico)
def buscar_veiculo(id_veiculo: int, session: SessionDep):

    veiculo = session.get(Veiculo, id_veiculo)
    
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")

    return veiculo

@app.patch("/veiculos/{id_veiculo}", response_model=VeiculoPublico)
def atualizar_veiculo(id_veiculo: int, dados: UpdateVeiculo, session: SessionDep):

    veiculo = session.get(Veiculo, id_veiculo)

    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")

    veiculo.sqlmodel_update(dados.model_dump(exclude_unset=True))
    session.add(veiculo)
    session.commit()
    session.refresh(veiculo)

    return veiculo


@app.delete("/veiculos/{id_veiculo}")
def deletar_veiculo(id_veiculo: int, session: SessionDep):

    veiculo = session.get(Veiculo, id_veiculo)

    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")

    session.delete(veiculo)
    session.commit()

    return {"mensagem": "Veículo deletado com sucesso."}





#rotas reservas

@app.post("/reservas", response_model=ReservaPublica)

def criar_reserva(reserva: CreateReserva, session: SessionDep):

    if not session.get(Usuario, reserva.id_usuario):
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if not session.get(Veiculo, reserva.id_veiculo):
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")

    # Verifica conflito de datas

    conflito = session.exec(
        select(Reserva).where(
            Reserva.id_veiculo == reserva.id_veiculo,
            Reserva.data_inicio < reserva.data_fim,
            Reserva.data_fim > reserva.data_inicio,
        )
    ).first()

    if conflito:
        raise HTTPException(status_code=409, detail="Veículo já reservado nesse período.")

    db_reserva = Reserva.model_validate(reserva)
    session.add(db_reserva)
    session.commit()
    session.refresh(db_reserva)

    return db_reserva


@app.get("/reservas", response_model=list[ReservaPublica])
def listar_reservas(session: SessionDep):
    return session.exec(select(Reserva)).all()



@app.get("/reservas/{id_reserva}", response_model=ReservaDetalhada)
def buscar_reserva(id_reserva: int, session: SessionDep):

    reserva = session.get(Reserva, id_reserva)

    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada.")

    usuario = session.get(Usuario, reserva.id_usuario)
    veiculo = session.get(Veiculo, reserva.id_veiculo)

    return ReservaDetalhada(
        id=reserva.id,
        data_inicio=reserva.data_inicio,
        data_fim=reserva.data_fim,
        nome_usuario=usuario.nome,
        modelo_veiculo=veiculo.modelo
    )



@app.patch("/reservas/{id_reserva}", response_model=ReservaPublica)
def atualizar_reserva(id_reserva: int, dados: UpdateReserva, session: SessionDep):

    reserva = session.get(Reserva, id_reserva)

    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada.")

    # Usa as novas datas se fornecidas, senão mantém as existentes

    nova_inicio = dados.data_inicio or reserva.data_inicio
    nova_fim = dados.data_fim or reserva.data_fim

    # Verifica conflito de datas excluindo a própria reserva

    conflito = session.exec(
        select(Reserva).where(
            Reserva.id_veiculo == reserva.id_veiculo,
            Reserva.id != id_reserva,
            Reserva.data_inicio < nova_fim,
            Reserva.data_fim > nova_inicio,
        )
    ).first()


    if conflito:
        raise HTTPException(status_code=409, detail="Veículo já reservado nesse período.")


    reserva.sqlmodel_update(dados.model_dump(exclude_unset=True))
    session.add(reserva)
    session.commit()
    session.refresh(reserva)
    
    return reserva

@app.get("/")
def servir_frontend():
    return FileResponse("index.html")

@app.delete("/reservas/{id_reserva}")
def deletar_reserva(id_reserva: int, session: SessionDep):

    reserva = session.get(Reserva, id_reserva)

    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada.")

    session.delete(reserva)
    session.commit()

    return {"mensagem": "Reserva deletada com sucesso."}