from abc import ABC, abstractmethod
from excepciones_y_logs import (
    DatoInvalidoError,
    ParametroFaltanteError,
    registrar_log,
)


class EntidadBase(ABC):
    """Clase abstracta base para las entidades generales de Software FJ."""

    def __init__(self, id_entidad: str) -> None:
        # Validamos que el identificador exista y no quede vacío
        if id_entidad is None or not str(id_entidad).strip():
            raise ParametroFaltanteError("El ID de la entidad es obligatorio.")
        self._id_entidad = str(id_entidad).strip()

    @property
    def id_entidad(self) -> str:
        """Permite leer el ID encapsulado sin modificarlo directamente."""
        return self._id_entidad

    @abstractmethod
    def resumen(self) -> str:
        """Cada clase hija debe implementar cómo se resume su información."""
        pass


class Cliente(EntidadBase):
    """Representa un cliente con datos personales encapsulados y validados."""

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(id_cliente)
        # Asignamos mediante propiedades (@property / @setter) para validar cada dato
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        limpio = str(valor).strip()
        if len(limpio) < 3:
            raise DatoInvalidoError(f"El nombre '{limpio}' es demasiado corto.")
        self._nombre = limpio

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El correo electrónico es obligatorio.")
        limpio = str(valor).strip()
        # Verificamos estructura básica con '@' y dominio con '.'
        if "@" not in limpio or "." not in limpio.split("@")[-1]:
            raise DatoInvalidoError(f"Correo electrónico inválido: '{limpio}'.")
        self._correo = limpio

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El teléfono del cliente es obligatorio.")
        limpio = str(valor).strip().replace("+", "").replace("-", "").replace(" ", "")
        if not limpio.isdigit() or len(limpio) < 7:
            raise DatoInvalidoError(f"Teléfono inválido: '{valor}'.")
        self._telefono = limpio

    def resumen(self) -> str:
        """Implementación del método abstracto heredado de EntidadBase."""
        return (
            f"Cliente [{self.id_entidad}] - {self.nombre} "
            f"| Correo: {self.correo} | Teléfono: {self.telefono}"
        )


if __name__ == "__main__":
    clientes_registrados = []

    # Caso válido
    try:
        cliente_ok = Cliente("CLI-01", "Laura Gómez", "laura.gomez@correo.com", "3104567890")
        clientes_registrados.append(cliente_ok)
        registrar_log("INFO", f"Cliente registrado: {cliente_ok.resumen()}")
        print("Registrado:", cliente_ok.resumen())
    except (DatoInvalidoError, ParametroFaltanteError) as err:
        registrar_log("ERROR", f"Error en cliente de prueba válido: {err}")
        print("Error:", err)

    # Caso inválido (correo sin '@')
    try:
        cliente_mal = Cliente("CLI-02", "Carlos Ruiz", "carlos.ruiz.correo.com", "3001112233")
        clientes_registrados.append(cliente_mal)
    except (DatoInvalidoError, ParametroFaltanteError) as err:
        registrar_log("ERROR", f"Intento inválido de cliente: {err}")
        print("Error controlado:", err)
