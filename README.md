# OrthoConnect

Entrega del **Proyecto Integrador / Parcial 2** de Ingeniería de Datos.

## Contenido del repositorio

| Archivo / carpeta | Qué es |
|---|---|
| `sql/schema.sql` | Esquema, funciones, triggers y vistas |
| `sql/seed.sql` | Datos de prueba |
| `src/main.py` | CLI con `psycopg2` |
| `src/repo.py` | Capa de acceso a datos |
| `DIAGRAMA_ER.md` | Diagrama entidad-relación |
| `DICCIONARIO_DE_DATOS.md` | Descripción de tablas y campos |
| `MANUAL_DE_USUARIO.md` | Cómo usar la aplicación |
| `EVIDENCIA_EJECUCION.md` | Capturas de ejecución real |

## Requisitos

- Python 3.11+
- PostgreSQL 12+

```bash
make setup          # crea .venv e instala dependencias
cp .env.example .env  # ajustar credenciales de PostgreSQL
make reset-db       # crea las tablas y carga los datos de prueba
```

## Ejecutar

```bash
make cli            # interfaz de línea de comando
make gui            # interfaz gráfica (opcional)
```

O directamente:

```bash
PYTHONPATH=. python -m src.main
```

## Reglas de negocio (implementadas en PostgreSQL)

- **Morosidad:** el trigger `trg_morosidad_agenda` bloquea agendar una cita si el paciente ya tiene dos o más citas anteriores sin pagar.
- **Eficacia:** `trg_eficacia_tratamiento` calcula `sesiones_estimadas / sesiones_asistidas * 100` cuando el tratamiento pasa a `FINALIZADO`.
- **Auditoría:** `trg_auditoria_evolucion` guarda valor anterior, valor nuevo, usuario y fecha cada vez que cambia `nota_evolucion`.
- **Pago FIFO:** `fn_aplicar_pago()` siempre salda la cita pendiente más antigua del tratamiento.

## Vistas analíticas

- `v_organigrama` — árbol de mando con CTE recursiva
- `v_cadena_referidos` — cadena paciente → referido con CTE recursiva
- `v_adherencia_detalle` + `v_reporte_adherencia` — días entre citas con `LAG`, clasificados ALTA / MEDIA / BAJA

## Pruebas

```bash
make test
```

15 pruebas, todas pasando. Cubren flujos demo, smoke test de CLI y validaciones reales sobre PostgreSQL.

## Notas sobre los datos de prueba

`seed.sql` contiene datos sintéticos derivados del enunciado y del ejemplo del profesor. Las secuencias están fijadas para que la demo reproduzca exactamente los IDs del ejemplo (`cita 14`, `pago 13`, eficacia `333.33%`). Para eso es necesario correr `make reset-db` antes de la demo.
