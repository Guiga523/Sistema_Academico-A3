from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from banco import (
    adicionar_aluno,
    atualizar_notas_aluno,
    excluir_aluno,
    listar_alunos,
)

ESTILO_NOTAS = """
QWidget#TelaNotas {
    background-color: #0f172a;
}

QFrame#Painel {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
}

QLabel {
    color: #e2e8f0;
    font-size: 13px;
}

QLabel#TituloTopo {
    color: #f8fafc;
    font-size: 20px;
    font-weight: 700;
}

QLabel#SubtituloTopo {
    color: #94a3b8;
    font-size: 13px;
}

QLineEdit, QDoubleSpinBox {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 13px;
}

QLineEdit:focus, QDoubleSpinBox:focus {
    border: 1px solid #3b82f6;
}

QPushButton#BtnPrimario {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#BtnPrimario:hover {
    background-color: #1d4ed8;
}

QPushButton#BtnSecundario {
    background-color: transparent;
    color: #cbd5e1;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 13px;
}

QPushButton#BtnSecundario:hover {
    background-color: #334155;
    color: #ffffff;
}

QPushButton#BtnPerigo {
    background-color: #991b1b;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#BtnPerigo:hover {
    background-color: #b91c1c;
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
    padding: 7px;
    border: none;
    font-weight: 600;
    font-size: 13px;
}
"""


class SistemaNotas(QWidget):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self.aluno_selecionado_id: int | None = None

        self.setObjectName("TelaNotas")
        self.setWindowTitle("Sistema Acadêmico - Alunos e Notas")
        self.resize(920, 560)
        self.setMinimumSize(720, 480)
        self.setStyleSheet(ESTILO_NOTAS)

        self._montar_interface()
        self._carregar_tabela()

    def _montar_interface(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(14)

        # Cabeçalho
        topo = QHBoxLayout()
        col_titulos = QVBoxLayout()
        titulo = QLabel("Gestão de Alunos e Notas")
        titulo.setObjectName("TituloTopo")
        subtitulo = QLabel(
            f"Usuário: {self.usuario['nome']} ({self.usuario['perfil']}) — Dados salvos em SQLite"
        )
        subtitulo.setObjectName("SubtituloTopo")
        col_titulos.addWidget(titulo)
        col_titulos.addWidget(subtitulo)

        btn_limpar_sel = QPushButton("Limpar campos")
        btn_limpar_sel.setObjectName("BtnSecundario")
        btn_limpar_sel.clicked.connect(self._limpar_campos)

        topo.addLayout(col_titulos)
        topo.addStretch()
        topo.addWidget(btn_limpar_sel)
        layout_principal.addLayout(topo)

        # Corpo: Formulário à esquerda + Tabela à direita
        corpo = QHBoxLayout()
        corpo.setSpacing(14)

        painel_form = QFrame()
        painel_form.setObjectName("Painel")
        painel_form.setFixedWidth(290)
        form_layout = QVBoxLayout(painel_form)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(8)

        lbl_form = QLabel("Dados do Aluno")
        lbl_form.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome completo")

        self.input_matricula = QLineEdit()
        self.input_matricula.setPlaceholderText("Ex.: 2026001")

        self.input_turma = QLineEdit()
        self.input_turma.setPlaceholderText("Ex.: 3º Semestre A")

        self.spin_nota1 = QDoubleSpinBox()
        self.spin_nota1.setRange(0.0, 10.0)
        self.spin_nota1.setDecimals(1)
        self.spin_nota1.setSingleStep(0.5)

        self.spin_nota2 = QDoubleSpinBox()
        self.spin_nota2.setRange(0.0, 10.0)
        self.spin_nota2.setDecimals(1)
        self.spin_nota2.setSingleStep(0.5)

        btn_adicionar = QPushButton("Adicionar Aluno")
        btn_adicionar.setObjectName("BtnPrimario")
        btn_adicionar.clicked.connect(self._salvar_novo_aluno)

        btn_atualizar_notas = QPushButton("Atualizar Notas do Selecionado")
        btn_atualizar_notas.setObjectName("BtnSecundario")
        btn_atualizar_notas.clicked.connect(self._atualizar_notas)

        btn_excluir = QPushButton("Excluir Aluno Selecionado")
        btn_excluir.setObjectName("BtnPerigo")
        btn_excluir.clicked.connect(self._excluir_selecionado)

        form_layout.addWidget(lbl_form)
        form_layout.addWidget(QLabel("Nome"))
        form_layout.addWidget(self.input_nome)
        form_layout.addWidget(QLabel("Matrícula"))
        form_layout.addWidget(self.input_matricula)
        form_layout.addWidget(QLabel("Turma"))
        form_layout.addWidget(self.input_turma)
        form_layout.addWidget(QLabel("Nota 1 (0 a 10)"))
        form_layout.addWidget(self.spin_nota1)
        form_layout.addWidget(QLabel("Nota 2 (0 a 10)"))
        form_layout.addWidget(self.spin_nota2)
        form_layout.addSpacing(8)
        form_layout.addWidget(btn_adicionar)
        form_layout.addWidget(btn_atualizar_notas)
        form_layout.addWidget(btn_excluir)
        form_layout.addStretch()

        # Tabela de alunos
        painel_tabela = QFrame()
        painel_tabela.setObjectName("Painel")
        tab_layout = QVBoxLayout(painel_tabela)
        tab_layout.setContentsMargins(18, 18, 18, 18)

        self.tabela = QTableWidget(0, 7)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Nome", "Matrícula", "Turma", "Nota 1", "Nota 2", "Média / Situação"]
        )
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.cellClicked.connect(self._selecionar_linha)

        tab_layout.addWidget(self.tabela)

        corpo.addWidget(painel_form)
        corpo.addWidget(painel_tabela)
        layout_principal.addLayout(corpo)

    def _carregar_tabela(self):
        alunos = listar_alunos()
        self.tabela.setRowCount(len(alunos))

        for linha_idx, aluno in enumerate(alunos):
            resumo = f"{aluno['media']:.1f} ({aluno['situacao']})"
            valores = [
                str(aluno["id"]),
                aluno["nome"],
                aluno["matricula"],
                aluno["turma"],
                f"{aluno['nota1']:.1f}",
                f"{aluno['nota2']:.1f}",
                resumo,
            ]
            for col_idx, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                if col_idx in (0, 2, 4, 5, 6):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabela.setItem(linha_idx, col_idx, item)

    def _selecionar_linha(self, row: int, _col: int):
        item_id = self.tabela.item(row, 0)
        if not item_id:
            return
        self.aluno_selecionado_id = int(item_id.text())
        self.input_nome.setText(self.tabela.item(row, 1).text())
        self.input_matricula.setText(self.tabela.item(row, 2).text())
        self.input_turma.setText(self.tabela.item(row, 3).text())
        self.spin_nota1.setValue(float(self.tabela.item(row, 4).text()))
        self.spin_nota2.setValue(float(self.tabela.item(row, 5).text()))

    def _salvar_novo_aluno(self):
        ok, msg, credenciais = adicionar_aluno(
            nome=self.input_nome.text(),
            matricula=self.input_matricula.text(),
            turma=self.input_turma.text(),
            nota1=self.spin_nota1.value(),
            nota2=self.spin_nota2.value(),
        )
        if not ok:
            QMessageBox.warning(self, "Atenção", msg)
            return

        if credenciais:
            QMessageBox.information(
                self,
                "Aluno e conta criados",
                f"{msg}\n\n"
                f"Aluno: {credenciais['nome']}\n"
                f"E-mail de acesso: {credenciais['email']}\n"
                f"Senha inicial: {credenciais['senha']}",
            )
        else:
            QMessageBox.information(self, "Sucesso", msg)

        self._limpar_campos()
        self._carregar_tabela()

    def _atualizar_notas(self):
        if self.aluno_selecionado_id is None:
            QMessageBox.warning(self, "Seleção necessária", "Clique em um aluno na tabela primeiro.")
            return

        ok, msg = atualizar_notas_aluno(
            aluno_id=self.aluno_selecionado_id,
            nota1=self.spin_nota1.value(),
            nota2=self.spin_nota2.value(),
        )
        if not ok:
            QMessageBox.warning(self, "Atenção", msg)
            return

        QMessageBox.information(self, "Sucesso", msg)
        self._carregar_tabela()

    def _excluir_selecionado(self):
        if self.aluno_selecionado_id is None:
            QMessageBox.warning(self, "Seleção necessária", "Clique em um aluno na tabela primeiro.")
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Deseja realmente excluir este aluno do banco?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        ok, msg = excluir_aluno(self.aluno_selecionado_id)
        if not ok:
            QMessageBox.warning(self, "Atenção", msg)
            return

        QMessageBox.information(self, "Removido", msg)
        self._limpar_campos()
        self._carregar_tabela()

    def _limpar_campos(self):
        self.aluno_selecionado_id = None
        self.input_nome.clear()
        self.input_matricula.clear()
        self.input_turma.clear()
        self.spin_nota1.setValue(0.0)
        self.spin_nota2.setValue(0.0)
        self.tabela.clearSelection()