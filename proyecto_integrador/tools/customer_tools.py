import os
import httpx

CUSTOMER_API_URL = os.getenv("CUSTOMER_API_URL", "http://127.0.0.1:8000")

DIAS_FACTURACION = 30

async def buscar_cliente_por_email(email:str) -> dict | None:

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{CUSTOMER_API_URL}/api/customers/", params={"email":email})
        response.raise_for_status()

    clientes = response.json()
    return clientes[0] if clientes else None


async def obtener_estado_de_cuenta(customer_id: int) -> dict:

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{CUSTOMER_API_URL}/api/customers/{customer_id}")
        response.raise_for_status()

    cliente = response.json()

    return {
        "balance": cliente["balance"],
        "balance_status": cliente["balance_status"]
    }


async def crear_reintegro(customer_id: int, monto: float, motivo:str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(f"{CUSTOMER_API_URL}/api/refunds/", json={"customer": customer_id, "amount": f"{monto:.2f}", "reason": motivo})
        response.raise_for_status()

    return response.json()

async def obtener_ultima_factura(customer_id: int) -> dict | None:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{CUSTOMER_API_URL}/api/customers/{customer_id}/invoices/",)
        response.raise_for_status()

    facturas = response.json()
    return facturas[0] if facturas else None


async def calcular_reintegro(customer_id:int, dias_sin_servicio: int, indice_malestar: float) -> dict:
    if dias_sin_servicio <= 0:
        raise ValueError("La cantidad de dias sin servicio debe ser positivo")

    indice = min(max(float(indice_malestar),1.0), 2.0)

    factura = await obtener_ultima_factura(customer_id)

    if factura is None:
        raise ValueError(f"El cliente {customer_id} no tiene facturas registradas")

    costo_diario = float(factura["amount"]) / DIAS_FACTURACION

    monto = dias_sin_servicio * costo_diario * indice

    reembolso = await crear_reintegro(
        customer_id, monto, f"{dias_sin_servicio} dia(s) sin servicio"
    )

    print(
        f"[herramienta] calcular_reintegro -> {dias_sin_servicio} día(s) x "
        f"${costo_diario:,.2f} x índice {indice} = ${monto:,.2f}"
    )

    return {
        "dias_sin_servicio": dias_sin_servicio,
        "costo_diario": round(costo_diario, 2),
        "indice_malestar": indice,
        "monto_reintegro": round(monto, 2),
        "reembolso": reembolso
    }


async def resetear_contrasena(customer_id: int) -> dict:
    """Resetea la contraseña de un cliente y envía un mail con el enlace para elegir una nueva.

    Args:
        customer_id: Id del cliente (ya identificado previamente con
            buscar_cliente_por_email).

    Returns:
        dict: Confirmación del envío, junto con la respuesta de customer_api
            (incluye el enlace de reseteo en reset_link).
    """
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            f"{CUSTOMER_API_URL}/api/customers/{customer_id}/reset_password/"
        )
        response.raise_for_status()

    resultado = response.json()

    print(
        f"[herramienta] resetear_contrasena -> Se ha enviado un mail con las "
        f"instrucciones para restablecer la contraseña del cliente {customer_id}."
    )

    return {"customer_id": customer_id, "estado": "mail de recuperación enviado", **resultado}


async def crear_interaccion(customer_id: int, content: str, query_type: str = "other") -> dict:
    """Registra en customer_api el resumen de una interacción con un cliente.

    Args:
        customer_id: Id del cliente (ya identificado previamente con
            buscar_cliente_por_email).
        content: Contenido de la interacción. Suele ser un JSON serializado
            como string con el detalle de la conversación, la encuesta de
            calidad y los análisis de sentimiento inicial y final.
        query_type: Tipo de consulta: 'customer_lookup', 'history',
            'password_reset', 'refund' u 'other' (default).

    Returns:
        dict: Interacción creada (incluye id, customer, content, query_type,
            created_at).
    """
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            f"{CUSTOMER_API_URL}/api/interactions/",
            json={"customer": customer_id, "content": content, "query_type": query_type}
        )
        response.raise_for_status()

    return response.json()
