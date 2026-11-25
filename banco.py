import hashlib
import os
import re
import sqlite3
import unicodedata
import hmac
from pathlib import Path

CAMINHO_DB = Path(__file__).resolve().parent / "sistema_academico.db"


def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(CAMINHO_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _gerar_hash_senha(senha: str, salt_hex: str | None = None) -> str:
    if salt_hex is None:
        salt_hex = os.urandom(16).hex()
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        bytes.fromhex(salt_hex),
        100_000,
    )
    return f"{salt_hex}${hash_bytes.hex()}"


def _verificar_senha(senha: str, senha_armazenada: str) -> bool:
    try:
        salt_hex, hash_esperado = senha_armazenada.split("$", 1)
    except ValueError:
        return False
    hash_calculado = _gerar_hash_senha(senha, salt_hex).split("$", 1)[1]
    return hmac.compare_digest(hash_calculado, hash_esperado)


def _normalizar_slug_nome(nome: str) -> str:
    sem_acentos = unicodedata.normalize("NFKD", nome.strip().lower())
    sem_acentos = "".join(c for c in sem_acentos if not unicodedata.combining(c))
    partes = [p for p in re.split(r"[^a-z0-9]+", sem_acentos) if p]
    if not partes:
        return "aluno"
    if len(partes) == 1:
        return partes[0]
    return f"".join(partes)


def _gerar_email_aluno(conn: sqlite3.Connection, nome: str) -> str:
    base = _normalizar_slug_nome(nome)
    dominio = "aluno.escola.edu.br"
    candidato = f"{base}@{dominio}"
    contador = 1

    while conn.execute("SELECT 1 FROM usuarios WHERE email = ?", (candidato,)).fetchone():
        contador += 1
        candidato = f"{base}{contador}@{dominio}"

    return candidato


def _gerar_senha_inicial(matricula: str) -> str:
    sufixo = os.urandom(2).hex()
    return f"{matricula.strip().upper()}#{sufixo}"


def _calcular_situacao(nota1: float, nota2: float) -> tuple[float, str]:
    media = round((nota1 + nota2) / 2, 2)
    if media >= 7.0:
        situacao = "Aprovado"
    elif media >= 5.0:
        situacao = "Recuperação"
    else:
        situacao = "Reprovado"
    return media, situacao


def inicializar_banco() -> None:
    with conectar() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                perfil TEXT NOT NULL CHECK (perfil IN ('Aluno', 'Professor', 'Coordenador')),
                senha_hash TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                nome TEXT NOT NULL,
                matricula TEXT NOT NULL UNIQUE,
                turma TEXT NOT NULL,
                nota1 REAL NOT NULL DEFAULT 0.0,
                nota2 REAL NOT NULL DEFAULT 0.0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE SET NULL
            );
            """
        )

        colunas = {
            row["name"] for row in conn.execute("PRAGMA table_info(alunos)").fetchall()
        }
        if "usuario_id" not in colunas:
            conn.execute("ALTER TABLE alunos ADD COLUMN usuario_id INTEGER;")

        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_alunos_usuario_id
            ON alunos (usuario_id);
            """
        )

        qtd = conn.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()["total"]
        if qtd == 0:
            conn.execute(
                """
                INSERT INTO usuarios (nome, email, perfil, senha_hash)
                VALUES (?, ?, ?, ?)
                """,
                (
                    "Administrador",
                    "admin@escola.edu.br",
                    "Coordenador",
                    _gerar_hash_senha("123"),
                ),
            )


def cadastrar_usuario(nome: str, email: str, perfil: str, senha: str) -> tuple[bool, str]:
    nome_limpo = nome.strip()
    email_limpo = email.strip().lower()

    if not nome_limpo or not email_limpo or not senha:
        return False, "Preencha nome, e-mail e senha."

    try:
        with conectar() as conn:
            conn.execute(
                """
                INSERT INTO usuarios (nome, email, perfil, senha_hash)
                VALUES (?, ?, ?, ?)
                """,
                (nome_limpo, email_limpo, perfil, _gerar_hash_senha(senha)),
            )
        return True, "Conta cadastrada com sucesso! Agora faça login."
    except sqlite3.IntegrityError:
        return False, "Já existe uma conta cadastrada com esse e-mail."
    except sqlite3.Error as erro:
        return False, f"Erro ao salvar no banco: {erro}"


def autenticar_usuario(email: str, senha: str) -> tuple[bool, dict | None]:
    email_limpo = email.strip().lower()

    with conectar() as conn:
        linha = conn.execute(
            "SELECT id, nome, email, perfil, senha_hash FROM usuarios WHERE LOWER(email) = ?",
            (email_limpo,),
        ).fetchone()

    if linha and _verificar_senha(senha, linha["senha_hash"]):
        return True, {
            "id": linha["id"],
            "nome": linha["nome"],
            "email": linha["email"],
            "perfil": linha["perfil"],
        }

    return False, None


def adicionar_aluno(
    nome: str,
    matricula: str,
    turma: str,
    nota1: float = 0.0,
    nota2: float = 0.0,
) -> tuple[bool, str, dict | None]:
    nome_limpo = nome.strip()
    matricula_limpa = matricula.strip().upper()
    turma_limpa = turma.strip()

    if not nome_limpo or not matricula_limpa or not turma_limpa:
        return False, "Preencha nome, matrícula e turma.", None

    for nota in (nota1, nota2):
        if nota < 0 or nota > 10:
            return False, "As notas devem estar entre 0.0 e 10.0.", None

    try:
        with conectar() as conn:
            existe_mat = conn.execute(
                "SELECT 1 FROM alunos WHERE matricula = ?", (matricula_limpa,)
            ).fetchone()
            if existe_mat:
                return False, "Já existe um aluno com essa matrícula.", None

            email_gerado = _gerar_email_aluno(conn, nome_limpo)
            senha_gerada = _gerar_senha_inicial(matricula_limpa)

            cursor_user = conn.execute(
                """
                INSERT INTO usuarios (nome, email, perfil, senha_hash)
                VALUES (?, ?, 'Aluno', ?)
                """,
                (nome_limpo, email_gerado, _gerar_hash_senha(senha_gerada)),
            )
            usuario_id = cursor_user.lastrowid

            conn.execute(
                """
                INSERT INTO alunos (usuario_id, nome, matricula, turma, nota1, nota2)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (usuario_id, nome_limpo, matricula_limpa, turma_limpa, nota1, nota2),
            )

        credenciais = {
            "nome": nome_limpo,
            "email": email_gerado,
            "senha": senha_gerada,
        }
        return True, "Aluno cadastrado e conta de acesso criada com sucesso!", credenciais
    except sqlite3.IntegrityError:
        return False, "Não foi possível cadastrar: matrícula ou e-mail já existem.", None
    except sqlite3.Error as erro:
        return False, f"Erro ao adicionar aluno: {erro}", None


def listar_alunos() -> list[dict]:
    with conectar() as conn:
        linhas = conn.execute(
            """
            SELECT a.id, a.nome, a.matricula, a.turma, a.nota1, a.nota2, u.email
            FROM alunos a
            LEFT JOIN usuarios u ON u.id = a.usuario_id
            ORDER BY a.nome ASC
            """
        ).fetchall()

    resultado = []
    for linha in linhas:
        media, situacao = _calcular_situacao(linha["nota1"], linha["nota2"])
        resultado.append(
            {
                "id": linha["id"],
                "nome": linha["nome"],
                "matricula": linha["matricula"],
                "turma": linha["turma"],
                "email": linha["email"] or "-",
                "nota1": linha["nota1"],
                "nota2": linha["nota2"],
                "media": media,
                "situacao": situacao,
            }
        )
    return resultado


def buscar_notas_do_aluno(usuario_id: int) -> dict | None:
    with conectar() as conn:
        linha = conn.execute(
            """
            SELECT nome, matricula, turma, nota1, nota2
            FROM alunos
            WHERE usuario_id = ?
            """,
            (usuario_id,),
        ).fetchone()

    if not linha:
        return None

    media, situacao = _calcular_situacao(linha["nota1"], linha["nota2"])
    return {
        "nome": linha["nome"],
        "matricula": linha["matricula"],
        "turma": linha["turma"],
        "nota1": linha["nota1"],
        "nota2": linha["nota2"],
        "media": media,
        "situacao": situacao,
    }


def atualizar_notas_aluno(aluno_id: int, nota1: float, nota2: float) -> tuple[bool, str]:
    for nota in (nota1, nota2):
        if nota < 0 or nota > 10:
            return False, "As notas devem estar entre 0.0 e 10.0."

    try:
        with conectar() as conn:
            cursor = conn.execute(
                """
                UPDATE alunos
                SET nota1 = ?, nota2 = ?
                WHERE id = ?
                """,
                (nota1, nota2, aluno_id),
            )
            if cursor.rowcount == 0:
                return False, "Aluno não encontrado."
        return True, "Notas atualizadas com sucesso!"
    except sqlite3.Error as erro:
        return False, f"Erro ao atualizar notas: {erro}"


def excluir_aluno(aluno_id: int) -> tuple[bool, str]:
    try:
        with conectar() as conn:
            linha = conn.execute(
                "SELECT usuario_id FROM alunos WHERE id = ?", (aluno_id,)
            ).fetchone()
            if not linha:
                return False, "Aluno não encontrado."

            conn.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
            if linha["usuario_id"] is not None:
                conn.execute("DELETE FROM usuarios WHERE id = ?", (linha["usuario_id"],))
        return True, "Aluno e conta de acesso removidos com sucesso!"
    except sqlite3.Error as erro:
        return False, f"Erro ao excluir aluno: {erro}"