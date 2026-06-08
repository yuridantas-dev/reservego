from sqlmodel import Field, SQLModel

# ─── USUÁRIO ──────────────────────────────────────────────

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
    tipo_usuario: str | None = None  # permite promover para admin via PATCH


# ─── VEÍCULO ──────────────────────────────────────────────

class VeiculoBase(SQLModel):
    marca: str
    modelo: str
    placa: str
    status: str
    preco_diaria: float = Field(default=150.0)  # ← adicionado

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
    preco_diaria: float | None = None  # ← adicionado


# ─── RESERVA ──────────────────────────────────────────────

class ReservaBase(SQLModel):
    id_usuario: int
    id_veiculo: int
    data_inicio: str
    data_fim: str

class Reserva(ReservaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    cancelada: bool = Field(default=False)  # ← adicionado

class ReservaPublica(ReservaBase):
    id: int
    cancelada: bool  # ← adicionado (frontend precisa saber)

class ReservaDetalhada(SQLModel):
    id: int
    data_inicio: str
    data_fim: str
    nome_usuario: str
    modelo_veiculo: str
    cancelada: bool  # ← adicionado

class CreateReserva(ReservaBase):
    pass

class UpdateReserva(SQLModel):
    data_inicio: str | None = None
    data_fim: str | None = None
    cancelada: bool | None = None  # ← adicionado (permite cancelar via PATCH)