import os
import subprocess
import datetime

# Configuração do nome do repositório (opcional)
REPO_DIR = os.path.dirname(os.path.abspath(__file__))  # Obtém o diretório atual
COMMIT_MESSAGE = f"Auto-update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"  # Mensagem com timestamp

def run_git_command(command):
    """Executa um comando Git e retorna a saída."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao executar comando: {command}")
        print(result.stderr)
    return result.stdout

def sync_repository():
    """Sincroniza o repositório local com o remoto no GitHub."""
    os.chdir(REPO_DIR)  # Garante que estamos no diretório correto

    # Verifica se há alterações no repositório
    status = run_git_command("git status --porcelain")
    
    if status.strip():
        print("🔄 Alterações detectadas. Commitando...")
        run_git_command("git add .")
        run_git_command(f'git commit -m "{COMMIT_MESSAGE}"')
    else:
        print("✅ Nenhuma alteração detectada. Repositório já está atualizado.")

    # Faz pull para garantir que o repositório local está atualizado
    print("⬇️  Fazendo pull das últimas alterações...")
    run_git_command("git pull origin main --rebase")

    # Faz push para enviar as alterações para o GitHub
    print("⬆️  Enviando alterações para o GitHub...")
    run_git_command("git push origin main")

    print("🚀 Repositório sincronizado com sucesso!")

if __name__ == "__main__":
    sync_repository()
