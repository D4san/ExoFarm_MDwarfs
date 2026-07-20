# `life_earth_sun_10pc`

Destino de los manifiestos de la Capa 1. La futura configuración debe leer los
perfiles Tierra--Sol A0--A3 canónicos desde `Transmission_Spectroscopy/profiles/`
y declarar por separado el forward de emisión y la escena LIFEsimMC/PHRINGE.

No hay resultados ni configuración ejecutable en esta carpeta aún.

> **Reanudación:** leer primero el [contrato de Etapa III](../../README.md), la [guía de reanudación](../../../docs/project_resume.md) y la [nota de procedencia N2O](../../../docs/earth_sun_n2o_matrix_provenance_2026-07-20.md). Este destino es solo para el benchmark `earth_20260615_pre_n2o_correction` hasta una decisión de rerun.

Los cuatro pares de entrada que deben registrarse por ruta y checksum son `Earth_A0_PreAgri_{PT,chem}.txt`, `Earth_A1_Current_{PT,chem}.txt`, `Earth_A2_Moderate_{PT,chem}.txt` y `Earth_A3_Extreme_{PT,chem}.txt` en `Transmission_Spectroscopy/profiles/`. No copiar ni regenerar perfiles para probar la interfaz.