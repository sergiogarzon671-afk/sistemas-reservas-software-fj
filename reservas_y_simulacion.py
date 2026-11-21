from entidades_cliente import Cliente, EntidadBase
from excepciones_y_logs import (
    CalculoInconsistenteError,
    DatoInvalidoError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    registrar_log,
)
from servicios import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    ReservaSala,
    Servicio,
)


class Reserva(EntidadBase):
    """Integra un cliente, un servicio, duración y estado con control de excepciones."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA")

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> None:
        super().__init__(id_reserva)

        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva requiere una instancia válida de Servicio.")

        try:
            horas = float(duracion_horas)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError(
                f"La duración '{duracion_horas}' debe ser un número."
            ) from exc

        # Validamos parámetros del servicio antes de crear la reserva
        servicio.validar_parametros(horas)

        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = horas
        self._descuento_pct = descuento_pct
        self._impuesto_pct = impuesto_pct
        self._estado = "PENDIENTE"
        self._costo_total = 0.0

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion_horas(self) -> float:
        return self._duracion_horas

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def confirmar(self) -> None:
        """Confirma la reserva verificando disponibilidad y calculando el costo."""
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva '{self.id_entidad}' porque está cancelada."
            )
        if self._estado == "CONFIRMADA":
            raise OperacionNoPermitidaError(
                f"La reserva '{self.id_entidad}' ya se encuentra confirmada."
            )
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' no está disponible para confirmar '{self.id_entidad}'."
            )

        self._costo_total = self._servicio.calcular_costo(
            self._duracion_horas,
            descuento_pct=self._descuento_pct,
            impuesto_pct=self._impuesto_pct,
        )
        self._servicio.disponible = False
        self._estado = "CONFIRMADA"

    def cancelar(self) -> None:
        """Cancela la reserva y libera el servicio si estaba confirmado."""
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError(
                f"La reserva '{self.id_entidad}' ya estaba cancelada."
            )
        if self._estado == "CONFIRMADA":
            self._servicio.disponible = True
        self._estado = "CANCELADA"

    def procesar_reserva(self) -> float:
        """Procesa la confirmación con try/except/else/finally y registra el resultado."""
        exito = False
        try:
            self.confirmar()
        except (
            ServicioNoDisponibleError,
            OperacionNoPermitidaError,
            DatoInvalidoError,
            CalculoInconsistenteError,
        ) as exc:
            registrar_log("ERROR", f"Error al procesar '{self.id_entidad}': {exc}")
            raise
        else:
            exito = True
            registrar_log(
                "INFO",
                f"Reserva '{self.id_entidad}' confirmada para '{self.cliente.nombre}' "
                f"({self.servicio.nombre}, {self.duracion_horas}h, total ${self.costo_total:.2f}).",
            )
            return self._costo_total
        finally:
            estado_final = "EXITOSO" if exito else "FALLIDO"
            registrar_log(
                "INFO",
                f"Fin de procesamiento de '{self.id_entidad}' -> {estado_final}.",
            )

    def resumen(self) -> str:
        return (
            f"Reserva [{self.id_entidad}] | Estado: {self._estado} "
            f"| Cliente: {self._cliente.nombre} | Servicio: {self._servicio.nombre} "
            f"| Duración: {self._duracion_horas}h | Total: ${self._costo_total:.2f}"
        )


def ejecutar_simulacion() -> None:
    """Ejecuta al menos 10 operaciones completas en memoria sin base de datos."""
    clientes: list[Cliente] = []
    servicios: list[Servicio] = []
    reservas: list[Reserva] = []

    print("=== SIMULACIÓN SISTEMA SOFTWARE FJ (12 OPERACIONES) ===\n")

    # Operación 1: Registro válido de cliente 1
    try:
        c1 = Cliente("CLI-01", "Ana María Pérez", "ana.perez@empresa.com", "3112223344")
        clientes.append(c1)
        registrar_log("INFO", f"Op 1 OK - Cliente registrado: {c1.resumen()}")
        print("Op 1 [OK]:", c1.resumen())
    except Exception as err:
        registrar_log("ERROR", f"Op 1 FALLO: {err}")
        print("Op 1 [FALLO]:", err)

    # Operación 2: Registro válido de cliente 2
    try:
        c2 = Cliente("CLI-02", "Juan David Torres", "juan.torres@correo.co", "3209876543")
        clientes.append(c2)
        registrar_log("INFO", f"Op 2 OK - Cliente registrado: {c2.resumen()}")
        print("Op 2 [OK]:", c2.resumen())
    except Exception as err:
        registrar_log("ERROR", f"Op 2 FALLO: {err}")
        print("Op 2 [FALLO]:", err)

    # Operación 3: Registro inválido de cliente (correo sin '@')
    try:
        c_mal = Cliente("CLI-03", "Pedro Malo", "pedro.correo.com", "3150001122")
        clientes.append(c_mal)
    except Exception as err:
        registrar_log("ERROR", f"Op 3 CONTROLADA - Cliente inválido: {err}")
        print("Op 3 [ERROR CONTROLADO]:", err)

    # Operación 4: Registro inválido de cliente (parámetro faltante)
    try:
        c_vacio = Cliente("CLI-04", "", "correo@valido.com", "3150001122")
        clientes.append(c_vacio)
    except Exception as err:
        registrar_log("ERROR", f"Op 4 CONTROLADA - Parámetro faltante: {err}")
        print("Op 4 [ERROR CONTROLADO]:", err)

    # Operación 5: Creación correcta de servicio ReservaSala
    try:
        s1 = ReservaSala("SRV-01", "Sala Ejecutiva A", 80.0, capacidad=12, disponible=True)
        servicios.append(s1)
        registrar_log("INFO", f"Op 5 OK - Servicio creado: {s1.describir()}")
        print("Op 5 [OK]:", s1.describir())
    except Exception as err:
        registrar_log("ERROR", f"Op 5 FALLO: {err}")
        print("Op 5 [FALLO]:", err)

    # Operación 6: Creación correcta de servicios AlquilerEquipo y AsesoriaEspecializada
    try:
        s2 = AlquilerEquipo("SRV-02", "Laptop Dev i7", 25.0, "Portátil", disponible=True)
        s3 = AsesoriaEspecializada("SRV-03", "Arquitectura Python", 120.0, "Backend & POO", disponible=True)
        servicios.extend([s2, s3])
        registrar_log("INFO", f"Op 6 OK - Servicios creados: {s2.id_entidad}, {s3.id_entidad}")
        print("Op 6 [OK]: Creados", s2.describir(), "|", s3.describir())
    except Exception as err:
        registrar_log("ERROR", f"Op 6 FALLO: {err}")
        print("Op 6 [FALLO]:", err)

    # Operación 7: Creación incorrecta de servicio (tarifa negativa / inconsistente)
    try:
        s_mal = ReservaSala("SRV-04", "Sala Beta", -50.0, capacidad=6)
        servicios.append(s_mal)
    except Exception as err:
        registrar_log("ERROR", f"Op 7 CONTROLADA - Servicio inválido: {err}")
        print("Op 7 [ERROR CONTROLADO]:", err)

    # Operación 8: Reserva exitosa con descuento e impuesto (sobrecarga de calcular_costo)
    try:
        r1 = Reserva("RES-01", clientes[0], servicios[0], duracion_horas=3, descuento_pct=10, impuesto_pct=19)
        r1.procesar_reserva()
        reservas.append(r1)
        print("Op 8 [OK]:", r1.resumen())
    except Exception as err:
        print("Op 8 [FALLO]:", err)

    # Operación 9: Segunda reserva exitosa de asesoría (sin descuento, con impuesto)
    try:
        r2 = Reserva("RES-02", clientes[1], servicios[2], duracion_horas=2, impuesto_pct=19)
        r2.procesar_reserva()
        reservas.append(r2)
        print("Op 9 [OK]:", r2.resumen())
    except Exception as err:
        print("Op 9 [FALLO]:", err)

    # Operación 10: Reserva fallida por servicio ya ocupado / no disponible
    try:
        r3 = Reserva("RES-03", clientes[1], servicios[0], duracion_horas=2)
        r3.procesar_reserva()
        reservas.append(r3)
    except Exception as err:
        print("Op 10 [ERROR CONTROLADO]:", err)

    # Operación 11: Reserva fallida por duración fuera de rango permitido
    try:
        r4 = Reserva("RES-04", clientes[0], servicios[1], duracion_horas=100)
        r4.procesar_reserva()
        reservas.append(r4)
    except Exception as err:
        registrar_log("ERROR", f"Op 11 CONTROLADA - Duración inválida: {err}")
        print("Op 11 [ERROR CONTROLADO]:", err)

    # Operación 12: Cancelación de reserva exitosa y liberación del servicio
    try:
        reservas[0].cancelar()
        registrar_log("INFO", f"Op 12 OK - Cancelada {reservas[0].id_entidad}; servicio {reservas[0].servicio.id_entidad} disponible={reservas[0].servicio.disponible}")
        print("Op 12 [OK]:", reservas[0].resumen(), "| Servicio disponible:", reservas[0].servicio.disponible)
    except Exception as err:
        registrar_log("ERROR", f"Op 12 FALLO: {err}")
        print("Op 12 [FALLO]:", err)

    print("\nResumen final en memoria -> Clientes:", len(clientes), "| Servicios:", len(servicios), "| Reservas:", len(reservas))


if __name__ == "__main__":
    ejecutar_simulacion()
