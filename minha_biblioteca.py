import sqlite3
import csv
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
BACKUP_DIR = BASE_DIR / 'backups'
EXPORT_DIR = BASE_DIR / 'exports'

DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / 'livraria.db'

def criar_conexao():
    return sqlite3.connect(DB_PATH)

def criar_tabela():
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER,
            preco REAL
        )
    ''')
    conn.commit()
    conn.close()

def adicionar_livro(titulo, autor, ano_publicacao, preco):
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)',
                   (titulo, autor, ano_publicacao, preco))
    conn.commit()
    conn.close()
    fazer_backup()

def exibir_livros():
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    conn.close()
    for livro in livros:
        print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: R${livro[4]:.2f}")

def atualizar_preco(id_livro, novo_preco):
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('UPDATE livros SET preco = ? WHERE id = ?', (novo_preco, id_livro))
    conn.commit()
    conn.close()
    fazer_backup()

def remover_livro(id_livro):
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM livros WHERE id = ?', (id_livro,))
    conn.commit()
    conn.close()
    fazer_backup()

def buscar_por_autor(autor):
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livros WHERE autor LIKE ?', (f'%{autor}%',))
    livros = cursor.fetchall()
    conn.close()
    for livro in livros:
        print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: R${livro[4]:.2f}")

def exportar_para_csv():
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    conn.close()

    csv_path = EXPORT_DIR / 'livros_exportados.csv'
    with open(csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
        csv_writer.writerows(livros)

def importar_de_csv():
    csv_path = EXPORT_DIR / 'livros_exportados.csv'
    conn = criar_conexao()
    cursor = conn.cursor()

    with open(csv_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  
        for row in csv_reader:
            cursor.execute('INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)',
                           (row[1], row[2], int(row[3]), float(row[4])))

    conn.commit()
    conn.close()
    fazer_backup()

def fazer_backup():
    data_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = BACKUP_DIR / f'backup_livraria_{data_atual}.db'
    
    import shutil
    shutil.copy2(DB_PATH, backup_path)

    backups = sorted(BACKUP_DIR.glob('backup_livraria_*.db'), key=os.path.getmtime, reverse=True)
    for backup in backups[5:]:
        os.remove(backup)

def menu():
    while True:
        print("\n----- Sistema de Gerenciamento de Livraria -----")
        print("1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            titulo = input("Título do livro: ")
            autor = input("Autor do livro: ")
            ano = int(input("Ano de publicação: "))
            preco = float(input("Preço do livro: "))
            adicionar_livro(titulo, autor, ano, preco)
        elif opcao == '2':
            exibir_livros()
        elif opcao == '3':
            id_livro = int(input("ID do livro: "))
            novo_preco = float(input("Novo preço: "))
            atualizar_preco(id_livro, novo_preco)
        elif opcao == '4':
            id_livro = int(input("ID do livro a ser removido: "))
            remover_livro(id_livro)
        elif opcao == '5':
            autor = input("Nome do autor: ")
            buscar_por_autor(autor)
        elif opcao == '6':
            exportar_para_csv()
            print("Dados exportados com sucesso")
        elif opcao == '7':
            importar_de_csv()
            print("Dados importados com sucesso.")
        elif opcao == '8':
            fazer_backup()
            print("Backup realizado com sucesso.")
        elif opcao == '9':
            print("Saindo do sistema.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    criar_tabela()
    menu()