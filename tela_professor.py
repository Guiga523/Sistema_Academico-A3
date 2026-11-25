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
    atualizar_notas_e_frequencia,
    listar_alunos,
)

ESTILO_PROFESSOR = """
QWidget#TelaProfessor {
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

QLineEdit:read-only {
    background-color: #162032;
    color: #94a3b8;
    border: 1px solid #293548;
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

QPushButton#BtnPrimario:disabled {
    background-color: #334155;
    color: #64748b;
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


class TelaProfessor(QWidget):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self.aluno_selecionado_id: int | None = None
        self.alunos_cache: list[dict] = []

        self.setObjectName("TelaProfessor")
        self.setWindowTitle("Portal do Professor - Alunos e Notas")
        self.resize(1020, 580)
        self.setMinimumSize(800, 500)
        self.setStyleSheet(ESTILO_PROFESSOR)

        self._montar_interface()
        self._carregar_tabela()

    def _montar_interface(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(14)

        topo = QHBoxLayout()
        col_titulos = QVBoxLayout()
        titulo = QLabel("Área do Professor — Lançamento de Notas e Frequência")
        titulo.setObjectName("TituloTopo")
        subtitulo = QLabel(
            f"Professor(a): {self.usuario['nome']}  •  Frequência abaixo de 75% leva o aluno à Recuperação"
        )
        subtitulo.setObjectName("SubtituloTopo")
        col_titulos.addWidget(titulo)
        col_titulos.addWidget(subtitulo)

        btn_novo = QPushButton("Novo Cadastro / Limpar")
        btn_novo.setObjectName("BtnSecundario")
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.clicked.connect(self._preparar_novo_cadastro)

        topo.addLayout(col_titulos)
        topo.addStretch()
        topo.addWidget(btn_novo)
        layout_principal.addLayout(topo)

        corpo = QHBoxLayout()
        corpo.setSpacing(14)

        painel_form = QFrame()
        painel_form.setObjectName("Painel")
        painel_form.setFixedWidth(310)
        form_layout = QVBoxLayout(painel_form)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(8)

        self.lbl_modo = QLabel("Cadastrar Novo Aluno")
        self.lbl_modo.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")

        self.lbl_aviso_bloqueio = QLabel(
            "Nome, matrícula e turma não podem ser alterados após o cadastro."
        )
        self.lbl_aviso_bloqueio.setWordWrap(True)
        self.lbl_aviso_bloqueio.setStyleSheet("font-size: 11px; color: #94a3b8;")

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

        self.spin_frequencia = QDoubleSpinBox()
        self.spin_frequencia.setRange(0.0, 100.0)
        self.spin_frequencia.setDecimals(1)
        self.spin_frequencia.setSingleStep(1.0)
        self.spin_frequencia.setValue(100.0)
        self.spin_frequencia.setSuffix("%")

        self.btn_adicionar = QPushButton("Cadastrar Aluno")
        self.btn_adicionar.setObjectName("BtnPrimario")
        self.btn_adicionar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_adicionar.clicked.connect(self._salvar_novo_aluno)

        self.btn_salvar_notas = QPushButton("Salvar Notas e Frequência")
        self.btn_salvar_notas.setObjectName("BtnSecundario")
        self.btn_salvar_notas.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_salvar_notas.clicked.connect(self._atualizar_notas_e_freq)

        form_layout.addWidget(self.lbl_modo)
        form_layout.addWidget(self.lbl_aviso_bloqueio)
        form_layout.addSpacing(4)
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
        form_layout.addWidget(QLabel("Frequência (0% a 100%)"))
        form_layout.addWidget(self.spin_frequencia)
        form_layout.addSpacing(8)
        form_layout.addWidget(self.btn_adicionar)
        form_layout.addWidget(self.btn_salvar_notas)
        form_layout.addStretch()

        painel_tabela = QFrame()
        painel_tabela.setObjectName("Painel")
        tab_layout = QVBoxLayout(painel_tabela)
        tab_layout.setContentsMargins(18, 18, 18, 18)
        tab_layout.setSpacing(10)

        barra_pesquisa = QHBoxLayout()
        barra_pesquisa.setSpacing(8)

        self.input_pesquisa = QLineEdit()
        self.input_pesquisa.setPlaceholderText("Pesquisar aluno por nome ou turma...")
        self.input_pesquisa.textChanged.connect(self._aplicar_filtro)

        btn_limpar_pesquisa = QPushButton("Limpar busca")
        btn_limpar_pesquisa.setObjectName("BtnSecundario")
        btn_limpar_pesquisa.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limpar_pesquisa.clicked.connect(self._limpar_pesquisa)

        barra_pesquisa.addWidget(self.input_pesquisa)
        barra_pesquisa.addWidget(btn_limpar_pesquisa)

        self.tabela = QTableWidget(0, 9)
        self.tabela.setHorizontalHeaderLabels(
            [
                "ID",
                "Nome",
                "Matrícula",
                "Turma",
                "E-mail",
                "Nota 1",
                "Nota 2",
                "Frequência",
                "Média / Situação",
            ]
        )
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.cellClicked.connect(self._selecionar_linha)

        tab_layout.addLayout(barra_pesquisa)
        tab_layout.addWidget(self.tabela)

        corpo.addWidget(painel_form)
        corpo.addWidget(painel_tabela)
        layout_principal.addLayout(corpo)

    def _carregar_tabela(self):
        self.alunos_cache = listar_alunos()
        self._aplicar_filtro()

    def _aplicar_filtro(self):
        termo = self.input_pesquisa.text().strip().lower()
        if not termo:
            alunos_filtrados = self.alunos_cache
        else:
            alunos_filtrados = [
                aluno
                for aluno in self.alunos_cache
                if termo in aluno["nome"].lower() or termo in aluno["turma"].lower()
            ]

        self.tabela.setRowCount(len(alunos_filtrados))

        for linha_idx, aluno in enumerate(alunos_filtrados):
            resumo = f"{aluno['media']:.1f} ({aluno['situacao']})"
            valores = [
                str(aluno["id"]),
                aluno["nome"],
                aluno["matricula"],
                aluno["turma"],
                aluno["email"],
                f"{aluno['nota1']:.1f}",
                f"{aluno['nota2']:.1f}",
                f"{aluno['frequencia']:.1f}%",
                resumo,
            ]
            for col_idx, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                if col_idx in (0, 2, 5, 6, 7, 8):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabela.setItem(linha_idx, col_idx, item)

    def _limpar_pesquisa(self):
        self.input_pesquisa.clear()

    def _selecionar_linha(self, row: int, _col: int):
        item_id = self.tabela.item(row, 0)
        if not item_id:
            return

        self.aluno_selecionado_id = int(item_id.text())
        self.lbl_modo.setText("Editando Notas e Frequência")

        self.input_nome.setText(self.tabela.item(row, 1).text())
        self.input_matricula.setText(self.tabela.item(row, 2).text())
        self.input_turma.setText(self.tabela.item(row, 3).text())

        self.input_nome.setReadOnly(True)
        self.input_matricula.setReadOnly(True)
        self.input_turma.setReadOnly(True)
        self.btn_adicionar.setEnabled(False)

        self.spin_nota1.setValue(float(self.tabela.item(row, 5).text()))
        self.spin_nota2.setValue(float(self.tabela.item(row, 6).text()))
        freq_texto = self.tabela.item(row, 7).text().replace("%", "").strip()
        self.spin_frequencia.setValue(float(freq_texto))

    def _preparar_novo_cadastro(self):
        self.aluno_selecionado_id = None
        self.lbl_modo.setText("Cadastrar Novo Aluno")

        self.input_nome.clear()
        self.input_matricula.clear()
        self.input_turma.clear()

        self.input_nome.setReadOnly(False)
        self.input_matricula.setReadOnly(False)
        self.input_turma.setReadOnly(False)
        self.btn_adicionar.setEnabled(True)

        self.spin_nota1.setValue(0.0)
        self.spin_nota2.setValue(0.0)
        self.spin_frequencia.setValue(100.0)
        self.tabela.clearSelection()

    def _salvar_novo_aluno(self):
        if self.aluno_selecionado_id is not None:
            QMessageBox.information(
                self,
                "Modo de edição",
                "Clique em 'Novo Cadastro / Limpar' antes de cadastrar outro aluno.",
            )
            return

        ok, msg, credenciais = adicionar_aluno(
            nome=self.input_nome.text(),
            matricula=self.input_matricula.text(),
            turma=self.input_turma.text(),
            nota1=self.spin_nota1.value(),
            nota2=self.spin_nota2.value(),
            frequencia=self.spin_frequencia.value(),
        )
        if not ok:
            QMessageBox.warning(self, "Atenção", msg)
            return

        if credenciais:
            QMessageBox.information(
                self,
                "Aluno cadastrado",
                f"{msg}\n\n"
                f"Aluno: {credenciais['nome']}\n"
                f"E-mail de acesso: {credenciais['email']}\n"
                f"Senha inicial: {credenciais['senha']}",
            )
        else:
            QMessageBox.information(self, "Sucesso", msg)

        self._preparar_novo_cadastro()
        self._carregar_tabela()

    def _atualizar_notas_e_freq(self):
        if self.aluno_selecionado_id is None:
            QMessageBox.warning(
                self,
                "Seleção necessária",
                "Clique em um aluno na tabela para lançar ou atualizar notas e frequência.",
            )
            return

        ok, msg = atualizar_notas_e_frequencia(
            aluno_id=self.aluno_selecionado_id,
            nota1=self.spin_nota1.value(),
            nota2=self.spin_nota2.value(),
            frequencia=self.spin_frequencia.value(),
        )
        if not ok:
            QMessageBox.warning(self, "Atenção", msg)
            return

        QMessageBox.information(self, "Sucesso", msg)
        self._carregar_tabela()