import platform
import sys


def main() -> None:
    """Print basic processor, memory, OS, and Python environment details."""
    try:
        import psutil

        memory_gb = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
    except ImportError:
        memory_gb = (
            "Biblioteca 'psutil' não instalada "
            "(execute 'pip install psutil' no terminal)"
        )

    print(
        f"Modelo do processador: {platform.processor() or platform.machine()}"
    )
    print(f"Quantidade de memória RAM: {memory_gb}")
    print(f"Sistema operacional: {platform.system()} {platform.release()}")
    print(f"Versão exata do Python: {sys.version.split()[0]}")


if __name__ == "__main__":
    main()
