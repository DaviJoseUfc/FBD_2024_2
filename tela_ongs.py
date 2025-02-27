import panel as pn
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, func
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuração da conexão com PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:123456@localhost:5432/projeto_ongs?client_encoding=utf8"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Definição da tabela ONG
class ONG(Base):
    __tablename__ = "ong"
    id_ong = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(14), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    telefone = Column(String(20))
    descricao = Column(Text)
    cidade = Column(String(100))
    bairro = Column(String(100))
    rua = Column(String(200))
    numero = Column(String(10))
    documentos_comprobatórios = Column(Text, name="documentos_comprobat¢rios")  # Nome exato da coluna no banco de dados

# Função para obter uma sessão do banco de dados
def get_session():
    return SessionLocal()

# Funções CRUD
def listar_ongs():
    session = get_session()
    ongs = session.query(ONG).order_by(ONG.id_ong).all()
    session.close()
    return [(o.id_ong, o.nome, o.cnpj, o.email, o.telefone, o.descricao, o.cidade, o.bairro, o.rua, o.numero, o.documentos_comprobatórios) for o in ongs]

def adicionar_ong(nome, cnpj, email, telefone, descricao, cidade, bairro, rua, numero, documentos_comprobatórios):
    session = get_session()
    ultimo_id = session.query(func.max(ONG.id_ong)).scalar() or 0
    proximo_id = ultimo_id + 1
    nova_ong = ONG(
        id_ong=proximo_id,
        nome=nome,
        cnpj=cnpj,
        email=email,
        telefone=telefone,
        descricao=descricao,
        cidade=cidade,
        bairro=bairro,
        rua=rua,
        numero=numero,
        documentos_comprobatórios=documentos_comprobatórios
    )
    session.add(nova_ong)
    session.commit()
    session.close()

def editar_ong(id_ong, **kwargs):
    session = get_session()
    ong = session.query(ONG).filter_by(id_ong=id_ong).first()
    if ong:
        for key, value in kwargs.items():
            if value:
                setattr(ong, key, value)
        session.commit()
    session.close()

def excluir_ong(id_ong):
    session = get_session()
    ong = session.query(ONG).filter_by(id_ong=id_ong).first()
    if ong:
        session.delete(ong)
        session.commit()
    session.close()

def consultar_ong(id_ong=None, nome=None, cnpj=None, cidade=None, bairro=None):  # Adicionado bairro
    session = get_session()
    
    query = session.query(ONG)
    
    if id_ong:
        query = query.filter(ONG.id_ong == id_ong)
    if nome:
        query = query.filter(ONG.nome.ilike(f"%{nome}%"))  # Busca aproximada
    if cnpj:
        query = query.filter(ONG.cnpj == cnpj)
    if cidade:
        query = query.filter(ONG.cidade.ilike(f"%{cidade}%"))  # Busca aproximada
    if bairro:  
        query = query.filter(ONG.bairro.ilike(f"%{bairro}%"))  # Adicionado filtro para bairro
    
    ongs = query.order_by(ONG.id_ong).all()
    
    session.close()

    if ongs:
        return [
            (o.id_ong, o.nome, o.cnpj, o.email, o.telefone, o.descricao, o.cidade, o.bairro, o.rua, o.numero, o.documentos_comprobatórios)
            for o in ongs
        ]
    else:
        return None

# Interface com Panel
pn.extension('tabulator')  # Carregar a extensão Tabulator

# Widgets de entrada
id_ong = pn.widgets.IntInput(name="ID", placeholder="Digite o ID", width=200)
nome = pn.widgets.TextInput(name="Nome", placeholder="Digite o nome", width=200)
cnpj = pn.widgets.TextInput(name="CNPJ", placeholder="Digite o CNPJ", width=200)
email = pn.widgets.TextInput(name="E-mail", placeholder="Digite o e-mail", width=200)
telefone = pn.widgets.TextInput(name="Telefone", placeholder="Digite o telefone", width=200)
descricao = pn.widgets.TextAreaInput(name="Descrição", placeholder="Digite a descrição", width=200, height=100)
cidade = pn.widgets.TextInput(name="Cidade", placeholder="Digite a cidade", width=200)
bairro = pn.widgets.TextInput(name="Bairro", placeholder="Digite o bairro", width=200)
rua = pn.widgets.TextInput(name="Rua", placeholder="Digite a rua", width=200)
numero = pn.widgets.TextInput(name="Número", placeholder="Digite o número", width=200)
documentos = pn.widgets.TextAreaInput(name="Documentos Comprobatórios", placeholder="Digite os documentos", width=200, height=100)

# Botões
button_consultar = pn.widgets.Button(name="Consultar", button_type="primary", width=100)
button_inserir = pn.widgets.Button(name="Inserir", button_type="success", width=100)
button_editar = pn.widgets.Button(name="Editar", button_type="warning", width=100)
button_excluir = pn.widgets.Button(name="Excluir", button_type="danger", width=100)

# Tabela de ONGs
def atualizar_tabela():
    data = listar_ongs()
    df = pd.DataFrame(data, columns=["ID", "Nome", "CNPJ", "E-mail", "Telefone", "Descrição", "Cidade", "Bairro", "Rua", "Número", "Documentos Comprobatórios"])
    return pn.widgets.Tabulator(df, width=1200)

tabela_ongs = atualizar_tabela()

# Callbacks
def consultar(event):
    resultado = consultar_ong(
        id_ong=id_ong.value if id_ong.value else None,
        nome=nome.value if nome.value else None,
        cnpj=cnpj.value if cnpj.value else None,
        cidade=cidade.value if cidade.value else None,
        bairro=bairro.value if bairro.value else None  # Adicionado
    )

    if resultado:
        texto = "\n\n".join([
            f"""
            **ID:** {r[0]}  
            **Nome:** {r[1]}  
            **CNPJ:** {r[2]}  
            **E-mail:** {r[3]}  
            **Telefone:** {r[4]}  
            **Descrição:** {r[5]}  
            **Cidade:** {r[6]}  
            **Bairro:** {r[7]}  
            **Rua:** {r[8]}  
            **Número:** {r[9]}  
            **Documentos Comprobatórios:** {r[10]}
            """
            for r in resultado
        ])
    else:
        texto = "Nenhuma ONG encontrada com os critérios informados."

    resultado_consulta.object = texto

def inserir(event):
    adicionar_ong(
        nome.value,
        cnpj.value,
        email.value,
        telefone.value,
        descricao.value,
        cidade.value,
        bairro.value,
        rua.value,
        numero.value,
        documentos.value
    )
    tabela_ongs.object = atualizar_tabela().object  # Atualiza a tabela

def editar(event):
    editar_ong(
        id_ong.value,
        nome=nome.value,
        cnpj=cnpj.value,
        email=email.value,
        telefone=telefone.value,
        descricao=descricao.value,
        cidade=cidade.value,
        bairro=bairro.value,
        rua=rua.value,
        numero=numero.value,
        documentos_comprobatórios=documentos.value
    )
    tabela_ongs.object = atualizar_tabela().object  # Atualiza a tabela

def excluir(event):
    excluir_ong(id_ong.value)
    tabela_ongs.object = atualizar_tabela().object  # Atualiza a tabela

# Vincular callbacks aos botões
button_consultar.on_click(consultar)
button_inserir.on_click(inserir)
button_editar.on_click(editar)
button_excluir.on_click(excluir)

# Painel de resultado da consulta
resultado_consulta = pn.pane.Markdown("", width=1200)

# Layout da interface
tela = pn.Column(
    "## Gerenciamento de ONGs",
    pn.Row(
        pn.Column(
            "### Campos de Entrada",
            id_ong,
            nome,
            cnpj,
            email,
            telefone,
            descricao,
            cidade,
            bairro,
            rua,
            numero,
            documentos,
            pn.Row(button_consultar, button_inserir, button_editar, button_excluir)
        ),
        pn.Column(
            "### Resultado da Consulta",
            resultado_consulta,
            "### Lista de ONGs",
            tabela_ongs
        )
    )
)

# Aplicar um tema (opcional)
pn.template.FastListTemplate(
    title="Gerenciamento de ONGs",
    main=[tela],
).servable()
