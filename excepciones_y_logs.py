from datetime import datetime
from pathlib import Path


# 1. Excepciones personalizadas para el sistema de Software FJ
class ErrorSoftwareFJ(Exception):
    """Clase base para los errores propios del sistema."""
    pass


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un dato ingresado no cumple con el formato o rango esperado."""
    pass


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se lanza cuando falta un dato obligatorio."""
    pass


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta una acción fuera de las reglas del negocio."""
    pass


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando un servicio no está disponible o ya está reservado."""
    pass


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando un cálculo de costo, descuento o tarifa es inconsistente."""
    pass


# 2. Función para escribir eventos y errores en el archivo de logs
def registrar_log(nivel: str, mensaje: str, archivo_log: str = "registro_software_fj.log") -> None:
    """Guarda eventos y errores con fecha y hora en un archivo de texto."""
    ruta = Path(archivo_log)
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{fecha_hora}] [{nivel.upper()}] {mensaje}\n"

    archivo = None
    try:
        # Abrimos en modo 'a' (append) para ir agregando registros sin borrar los anteriores
        archivo = open(ruta, mode="a", encoding="utf-8")
        archivo.write(linea)
    except OSError as exc:
        # Si hay un problema al escribir el archivo, evitamos que el programa se detenga
        print(f"Aviso: no se pudo escribir en el log -> {exc}")
    finally:
        # Garantizamos el cierre del archivo aunque ocurra algún error
        if archivo is not None and not archivo.closed:
            archivo.close()


if __name__ == "__main__":
    # Ejemplo sencillo de try/except/else/finally y encadenamiento de excepciones
    try:
        duracion_texto = "tres"  # Dato inválido a propósito para probar el manejo de errores
        try:
            duracion = float(duracion_texto)
        except ValueError as error_original:
            # Encadenamos el ValueError original con nuestra excepción personalizada
            raise DatoInvalidoError(
                f"La duración '{duracion_texto}' no es un número válido."
            ) from error_original
    except DatoInvalidoError as err:
        registrar_log("ERROR", f"{err} | Causa original: {err.__cause__}")
        print("Error controlado y registrado:", err)
    else:
        print("Operación completada sin errores.")
    finally:
        print("Bloque finally ejecutado: prueba de registro de log finalizada.")
