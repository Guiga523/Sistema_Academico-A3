from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from banco import buscar_notas_do_aluno

ESTILO_ALUNO = """
QWidget#TelaAluno {
    background-color: #0f172a;
}

QFrame#CardAluno {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
}

QLabel {
    color: #e2e8f0;
    font-size: 13px;
}

QLabel#TituloAluno {
    color: #f8fafc;
    font-size: 20px;
    font-weight: 700;
}

QLabel#SubtituloAluno {
    color: #94a3b8;
    font-size: 13px;
}

QTableWidget {
    background-color: #0f172a;
    color: #f8fafc;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 8px;
    font-size: 13px;
}

QHeaderView::section {
    background-color: #334155;
    color: #f8fafc;
    padding: 8px;
    border: none;
    font-weight: 600;
    font-size: 13px;
}
"""


class TelaAluno(QWidget):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario

        self.setObjectName("TelaAluno")
        self.setWindowTitle("Portal do Aluno - Minhas Notas")
        self.resize(680, 420)
        self.setMinimumSize(520, 340)
        self.setStyleSheet(ESTILO_ALUNO)

        self._montar_interface()
        self._carregar_notas()

    def _montar_interface(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        layout_principal.addStretch()
        linha_central = QHBoxLayout()
        linha_central.addStretch()

        card = QFrame()
        card.setObjectName("CardAluno")
        card.setMaximumWidth(620)
        card.setMinimumWidth(460)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)

        titulo = QLabel("Minhas Notas")
        titulo.setObjectName("TituloAluno")

        self.lbl_info = QLabel(
            f"Aluno(a): {self.usuario['nome']} | E-mail: {self.usuario['email']}"
        )
        self.lbl_info.setObjectName("SubtituloAluno")

        self.lbl_detalhes = QLabel("Carregando dados da matrícula...")
        self.lbl_detalhes.setObjectName("SubtituloAluno")

        self.tabela_notas = QTableWidget(0, 4)
        self.tabela_notas.setHorizontalHeaderLabels(["Nota 1", "Nota 2","Frequência", "Média", "Situação"])
        self.tabela_notas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela_notas.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tabela_notas.verticalHeader().setVisible(False)
        self.tabela_notas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_notas.setFixedHeight(86)

        card_layout.addWidget(titulo)
        card_layout.addWidget(self.lbl_info)
        card_layout.addWidget(self.lbl_detalhes)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.tabela_notas)

        linha_central.addWidget(card)
        linha_central.addStretch()
        layout_principal.addLayout(linha_central)
        layout_principal.addStretch()

    def _carregar_notas(self):
        dados = buscar_notas_do_aluno(self.usuario["id"])
        if not dados:
            self.lbl_detalhes.setText(
                "Nenhuma ficha de notas vinculada a esta conta ainda."
            )
            self.tabela_notas.setRowCount(0)
            return

        self.lbl_detalhes.setText(
            f"Matrícula: {dados['matricula']}  •  Turma: {dados['turma']}"
        )
        self.tabela_notas.setRowCount(1)

        valores = [
            f"{dados['nota1']:.1f}",
            f"{dados['nota2']:.1f}",
            f"{dados['frequencia']:.1f}%",
            f"{dados['media']:.1f}",
            dados["situacao"],
        ]
        for col, texto in enumerate(valores):
            item = QTableWidgetItem(texto)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabela_notas.setItem(0, col, item)