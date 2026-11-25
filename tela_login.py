import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from banco import autenticar_usuario, cadastrar_usuario, inicializar_banco

ESTILO_QSS = """
QWidget#JanelaPrincipal {
    background-color: #0f172a;
}

QFrame#Card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
}

QLabel {
    color: #e2e8f0;
    font-size: 13px;
}

QLabel#Titulo {
    color: #f8fafc;
    font-size: 22px;
    font-weight: 700;
}

QLabel#Subtitulo {
    color: #94a3b8;
    font-size: 13px;
}

QLineEdit, QComboBox {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 9px 12px;
    font-size: 13px;
    min-height: 20px;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QPushButton#BotaoPrimario {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 600;
    min-height: 22px;
}

QPushButton#BotaoPrimario:hover {
    background-color: #1d4ed8;
}

QPushButton#BotaoPrimario:pressed {
    background-color: #1e40af;
}

QPushButton#BotaoSecundario {
    background-color: transparent;
    color: #cbd5e1;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 500;
    min-height: 22px;
}

QPushButton#BotaoSecundario:hover {
    background-color: #334155;
    color: #ffffff;
}
"""


class TelaLogin(QWidget):
    login_sucesso = Signal(dict)

    def __init__(self):
        super().__init__()
        inicializar_banco()

        self.setObjectName("JanelaPrincipal")
        self.setWindowTitle("Sistema Acadêmico - Acesso")
        self.resize(520, 460)
        self.setMinimumSize(380, 380)
        self.setStyleSheet(ESTILO_QSS)

        self.stack = QStackedWidget()
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.addWidget(self.stack)

        self.stack.addWidget(self._criar_card(self._conteudo_tela_inicial()))   # índice 0
        self.stack.addWidget(self._criar_card(self._conteudo_tela_login()))     # índice 1
        self.stack.addWidget(self._criar_card(self._conteudo_tela_cadastro()))  # índice 2

        self.stack.setCurrentIndex(0)

    def _criar_card(self, conteudo_widget: QWidget) -> QWidget:
        container = QWidget()
        layout_externo = QVBoxLayout(container)
        layout_externo.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("Card")
        card.setMaximumWidth(380)
        card.setMinimumWidth(300)

        layout_card = QVBoxLayout(card)
        layout_card.setContentsMargins(26, 26, 26, 26)
        layout_card.addWidget(conteudo_widget)

        layout_externo.addStretch()
        linha_central = QHBoxLayout()
        linha_central.addStretch()
        linha_central.addWidget(card)
        linha_central.addStretch()
        layout_externo.addLayout(linha_central)
        layout_externo.addStretch()

        return container

    def _conteudo_tela_inicial(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        titulo = QLabel("Sistema Acadêmico")
        titulo.setObjectName("Titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitulo = QLabel("Gestão de Alunos e Notas")
        subtitulo.setObjectName("Subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_logar = QPushButton("Logar")
        btn_logar.setObjectName("BotaoPrimario")
        btn_logar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logar.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        btn_criar_conta = QPushButton("Criar conta")
        btn_criar_conta.setObjectName("BotaoSecundario")
        btn_criar_conta.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_criar_conta.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(12)
        layout.addWidget(btn_logar)
        layout.addWidget(btn_criar_conta)

        return widget

    def _conteudo_tela_login(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        titulo = QLabel("Logar")
        titulo.setObjectName("Titulo")

        subtitulo = QLabel("Entre com suas credenciais para acessar.")
        subtitulo.setObjectName("Subtitulo")

        self.input_login_email = QLineEdit()
        self.input_login_email.setPlaceholderText("E-mail")

        self.input_login_senha = QLineEdit()
        self.input_login_senha.setPlaceholderText("Senha")
        self.input_login_senha.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_ver_senha = QPushButton("Mostrar")
        self.btn_ver_senha.setObjectName("BotaoSecundario")
        self.btn_ver_senha.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ver_senha.setFixedWidth(85)
        self.btn_ver_senha.clicked.connect(self._alternar_visibilidade_senha)

        linha_senha = QHBoxLayout()
        linha_senha.setSpacing(6)
        linha_senha.addWidget(self.input_login_senha)
        linha_senha.addWidget(self.btn_ver_senha)

        btn_confirmar_login = QPushButton("Entrar")
        btn_confirmar_login.setObjectName("BotaoPrimario")
        btn_confirmar_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirmar_login.clicked.connect(self._processar_login)

        btn_voltar = QPushButton("Voltar")
        btn_voltar.setObjectName("BotaoSecundario")
        btn_voltar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_voltar.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(8)
        layout.addWidget(QLabel("E-mail"))
        layout.addWidget(self.input_login_email)
        layout.addWidget(QLabel("Senha"))
        layout.addLayout(linha_senha)
        layout.addSpacing(8)
        layout.addWidget(btn_confirmar_login)
        layout.addWidget(btn_voltar)

        return widget

    def _conteudo_tela_cadastro(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        titulo = QLabel("Criar conta")
        titulo.setObjectName("Titulo")

        subtitulo = QLabel("Cadastre-se para começar a usar o sistema.")
        subtitulo.setObjectName("Subtitulo")

        self.input_cad_nome = QLineEdit()
        self.input_cad_nome.setPlaceholderText("Nome completo")

        self.input_cad_email = QLineEdit()
        self.input_cad_email.setPlaceholderText("E-mail")

        self.combo_cad_perfil = QComboBox()
        self.combo_cad_perfil.addItems(["Aluno", "Professor"])

        self.input_cad_senha = QLineEdit()
        self.input_cad_senha.setPlaceholderText("Crie uma senha")
        self.input_cad_senha.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_ver_cad_senha = QPushButton("Mostrar")
        self.btn_ver_cad_senha.setObjectName("BotaoSecundario")
        self.btn_ver_cad_senha.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ver_cad_senha.setFixedWidth(85)
        self.btn_ver_cad_senha.clicked.connect(self._alternar_visibilidade_cad_senha)

        linha_cad_senha = QHBoxLayout()
        linha_cad_senha.setSpacing(6)
        linha_cad_senha.addWidget(self.input_cad_senha)
        linha_cad_senha.addWidget(self.btn_ver_cad_senha)

        linha_botoes = QHBoxLayout()
        btn_salvar = QPushButton("Cadastrar")
        btn_salvar.setObjectName("BotaoPrimario")
        btn_salvar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salvar.clicked.connect(self._processar_cadastro)

        btn_voltar = QPushButton("Voltar")
        btn_voltar.setObjectName("BotaoSecundario")
        btn_voltar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_voltar.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        linha_botoes.addWidget(btn_salvar)
        linha_botoes.addWidget(btn_voltar)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(6)
        layout.addWidget(QLabel("Nome"))
        layout.addWidget(self.input_cad_nome)
        layout.addWidget(QLabel("E-mail"))
        layout.addWidget(self.input_cad_email)
        layout.addWidget(QLabel("Perfil"))
        layout.addWidget(self.combo_cad_perfil)
        layout.addWidget(QLabel("Senha"))
        layout.addLayout(linha_cad_senha)
        layout.addSpacing(8)
        layout.addLayout(linha_botoes)

        return widget

    def _alternar_visibilidade_senha(self):
        visivel = self.input_login_senha.echoMode() == QLineEdit.EchoMode.Normal
        if visivel:
            self.input_login_senha.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_ver_senha.setText("Mostrar")
        else:
            self.input_login_senha.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_ver_senha.setText("Ocultar")

    def _alternar_visibilidade_cad_senha(self):
        visivel = self.input_cad_senha.echoMode() == QLineEdit.EchoMode.Normal
        if visivel:
            self.input_cad_senha.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_ver_cad_senha.setText("Mostrar")
        else:
            self.input_cad_senha.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_ver_cad_senha.setText("Ocultar")

    def _processar_login(self):
        email = self.input_login_email.text().strip().lower()
        senha = self.input_login_senha.text()

        ok, usuario = autenticar_usuario(email, senha)
        if ok and usuario:
            self.input_login_senha.clear()
            self.input_login_senha.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_ver_senha.setText("Mostrar")
            QMessageBox.information(
                self,
                "Acesso permitido",
                f"Bem-vindo(a), {usuario['nome']} ({usuario['perfil']})!",
            )
            self.hide()
            self.login_sucesso.emit(usuario)
        else:
            QMessageBox.warning(
                self,
                "Erro de login",
                "E-mail ou senha inválidos. Verifique se o e-mail está exatamente como foi gerado ou cadastrado.",
            )

    def _processar_cadastro(self):
        nome = self.input_cad_nome.text()
        email = self.input_cad_email.text()
        perfil = self.combo_cad_perfil.currentText()
        senha = self.input_cad_senha.text()

        ok, mensagem = cadastrar_usuario(nome, email, perfil, senha)
        if not ok:
            QMessageBox.warning(self, "Atenção", mensagem)
            return

        QMessageBox.information(self, "Conta criada", mensagem)
        self.input_cad_nome.clear()
        self.input_cad_email.clear()
        self.input_cad_senha.clear()
        self.input_cad_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_ver_cad_senha.setText("Mostrar")
        self.stack.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TelaLogin()
    janela.show()
    sys.exit(app.exec())