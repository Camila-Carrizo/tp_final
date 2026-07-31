"""
main.py
-------
Arranca el programa.
"""

from simulador import ejecutar


def main() -> None:
    estado = ejecutar()
    print("Fila inicial:")
    for clave, valor in estado.items():
        print(f"  {clave}: {valor}")


if __name__ == "__main__":
    main()
