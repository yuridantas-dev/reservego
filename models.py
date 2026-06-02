from sqlmodel import Field, SQLModel

#Diminuir codigo, colocando todos os atributos dentro da classe

#usuário
class UsuarioBase(SQLModel):
    nome: str
    cpf: str
    email: str
    cnh: str
    tipo_usuario: str

class Usuario(UsuarioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    senha: str

class UsuarioPublico(UsuarioBase):
    id: int

class CreateUsuario(UsuarioBase):
    senha: str

class UpdateUsuario(SQLModel):
    nome: str | None = None
    email: str | None = None
    senha: str | None = None

#veículo
class VeiculoBase(SQLModel):
    marca: str
    modelo: str
    placa: str
    status: str

class Veiculo(VeiculoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class VeiculoPublico(VeiculoBase):
    id: int

class CreateVeiculo(VeiculoBase):
    pass

class UpdateVeiculo(SQLModel):
    marca: str | None = None
    modelo: str | None = None
    placa: str | None = None
    status: str | None = None

#reserva
class ReservaBase(SQLModel):
    id_usuario: int
    id_veiculo: int
    data_inicio: str
    data_fim: str

class Reserva(ReservaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class ReservaPublica(ReservaBase):
    id: int

class ReservaDetalhada(SQLModel):
    id: int
    data_inicio: str
    data_fim: str
    nome_usuario: str
    modelo_veiculo: str

class CreateReserva(ReservaBase):
    pass

class UpdateReserva(SQLModel):
    data_inicio: str | None = None
    data_fim: str | None = None
