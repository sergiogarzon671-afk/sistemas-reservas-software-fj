from abc import abstractmethod
from entidades_cliente import EntidadBase
from excepciones_y_logs import (
    CalculoInconsistenteError,
    DatoInvalidoError,
    ParametroFaltanteError,
)


class Servicio(EntidadBase):
    """Clase abstracta base para los servicios que ofrece Software FJ."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio)
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        self._nombre = str(valor).strip()

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: float) -> None:
        try:
            tarifa = float(valor)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError(f"La tarifa base '{valor}' debe ser numérica.") from exc
        if tarifa <= 0:
            raise CalculoInconsistenteError("La tarifa base debe ser mayor que cero.")
        self._tarifa_base = tarifa

    @abstractmethod
    def validar_parametros(self, duracion_horas: float) -> None:
        """Valida si la duración o parámetros son válidos para este servicio."""
        pass

    @abstractmethod
    def calcular_costo_base(self, duracion_horas: float) -> float:
        """Calcula el costo base antes de descuentos o impuestos."""
        pass

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción clara del servicio."""
        pass

    # Sobrecarga simulada en Python mediante argumentos opcionales con valor por defecto:
    # - calcular_costo(horas) -> costo base con parámetros por defecto
    # - calcular_costo(horas, descuento_pct=10) -> con descuento
    # - calcular_costo(horas, descuento_pct=10, impuesto_pct=19) -> con descuento e impuesto
    def calcular_costo(
        self,
        duracion_horas: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        """Calcula el costo final admitiendo descuento e impuesto opcionales."""
        try:
            horas = float(duracion_horas)
            descuento = float(descuento_pct)
            impuesto = float(impuesto_pct)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError(
                "La duración, el descuento o el impuesto deben ser valores numéricos."
            ) from exc

        self.validar_parametros(horas)
        subtotal = self.calcular_costo_base(horas)

        if descuento < 0 or descuento > 100 or impuesto < 0:
            raise CalculoInconsistenteError(
                "Porcentaje de descuento (0-100) o impuesto inválido."
            )

        con_descuento = subtotal * (1 - descuento / 100.0)
        total = con_descuento * (1 + impuesto / 100.0)

        if total < 0:
            raise CalculoInconsistenteError("El costo total no puede ser negativo.")
        return round(total, 2)

    def resumen(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"Servicio [{self.id_entidad}] {self.nombre} "
            f"| Tarifa base: ${self.tarifa_base:.2f} | {estado}"
        )


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas de reuniones o capacitación."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        capacidad: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if capacidad <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser mayor que cero.")
        self.capacidad = capacidad

    def validar_parametros(self, duracion_horas: float) -> None:
        if duracion_horas <= 0 or duracion_horas > 12:
            raise DatoInvalidoError("La reserva de sala debe durar entre 1 y 12 horas.")

    def calcular_costo_base(self, duracion_horas: float) -> float:
        # Si pasa de 4 horas, sumamos un 10 % adicional por logística de sala
        factor_extra = 1.10 if duracion_horas > 4 else 1.0
        return self.tarifa_base * duracion_horas * factor_extra

    def describir(self) -> str:
        return f"Reserva de Sala '{self.nombre}' (capacidad: {self.capacidad}) -> {self.resumen()}"


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos tecnológicos."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        tipo_equipo: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not tipo_equipo or not str(tipo_equipo).strip():
            raise ParametroFaltanteError("El tipo de equipo es obligatorio.")
        self.tipo_equipo = str(tipo_equipo).strip()

    def validar_parametros(self, duracion_horas: float) -> None:
        if duracion_horas < 1 or duracion_horas > 72:
            raise DatoInvalidoError("El alquiler de equipo debe durar entre 1 y 72 horas.")

    def calcular_costo_base(self, duracion_horas: float) -> float:
        return self.tarifa_base * duracion_horas

    def describir(self) -> str:
        return f"Alquiler de Equipo [{self.tipo_equipo}] '{self.nombre}' -> {self.resumen()}"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas o de desarrollo de software."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not especialidad or not str(especialidad).strip():
            raise ParametroFaltanteError("La especialidad de la asesoría es obligatoria.")
        self.especialidad = str(especialidad).strip()

    def validar_parametros(self, duracion_horas: float) -> None:
        if duracion_horas < 0.5 or duracion_horas > 20:
            raise DatoInvalidoError("La asesoría debe durar entre 0.5 y 20 horas.")

    def calcular_costo_base(self, duracion_horas: float) -> float:
        return self.tarifa_base * duracion_horas

    def describir(self) -> str:
        return f"Asesoría en {self.especialidad} ('{self.nombre}') -> {self.resumen()}"
