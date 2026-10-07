import platform
import sys

# Tenta importar o psutil para ler a memória RAM
try:
    import psutil
    ram_gb = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
except ImportError:
    ram_gb = "Biblioteca 'psutil' não instalada (execute 'pip install psutil' no terminal)"

# Exibe os resultados organizados
print(f"Modelo do processador: {platform.processor() or platform.machine()}")
print(f"Quantidade de memória RAM: {ram_gb}")
print(f"Sistema operacional: {platform.system()} {platform.release()}")
print(f"Versão exata do Python: {sys.version.split()[0]}")
