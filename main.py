import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget
from banco import inicializar_banco
from sistema_notas import SistemaNotas
from tela_aluno import TelaAluno
from tela_login import TelaLogin


def main():
    inicializar_banco()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    janela_login = TelaLogin()
    janela_destino: QWidget | None = None

    def abrir_sistema(usuario: dict):
        nonlocal janela_destino
        try:
            if usuario["perfil"] == "Aluno":
                janela_destino = TelaAluno(usuario)
            else:
                janela_destino = SistemaNotas(usuario)
            janela_destino.show()
        except Exception as erro:
            QMessageBox.critical(
                None,
                "Erro ao abrir tela",
                f"Ocorreu um erro ao carregar a tela de {usuario['perfil']}:\n{erro}",
            )
            janela_login.show()

    janela_login.login_sucesso.connect(abrir_sistema)
    janela_login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()