import numpy as np

# Constantes físicas
AU_cm = 1.495978707e13
PC_cm = 3.08567758e18
D_star_pc = 12.47
D_star_cm = D_star_pc * PC_cm

R_sun_cm = 6.957e10
R_star_Rs = 0.117
R_star_cm = R_star_Rs * R_sun_cm

# Factor geométrico: (Distancia_Tierra_Estrella / Radio_Estrella)^2
# El archivo original tiene flujo OBSERVADO en la Tierra (a 12.47 pc).
# Queremos flujo en la SUPERFICIE de la estrella.
geometric_scale = (D_star_cm / R_star_cm)**2

# Factor de unidades: Angstrom -> nm
# Flujo por nm = 10 * Flujo por Angstrom
unit_scale = 10.0

# Factor Total Esperado
total_expected_factor = geometric_scale * unit_scale

print(f"--- Verificación de Factores ---")
print(f"Radio de TRAPPIST-1: {R_star_cm:.4e} cm")
print(f"Distancia (12.47 pc):{D_star_cm:.4e} cm")
print(f"Factor Geométrico:   {geometric_scale:.4e}")
print(f"Factor Unidades:     {unit_scale:.1f}")
print(f"Factor TOTAL Teórico:{total_expected_factor:.4e}")
print(f"----------------------------\n")

# Archivos
original_file = r'c:/Users/User/Documents/obsidian/DASAN/01 Temas/Academia/Maestría/Formación Planetaria/Proyecto final/trappist-1_model_const_res_v07.ecsv'
processed_file = r'c:/Users/User/Documents/obsidian/DASAN/01 Temas/Academia/Maestría/Formación Planetaria/Proyecto final/VULCAN/stars/trappist1_megamuscles.dat'

# Leer datos originales (muestreo)
print("Leyendo archivo original...")
orig_data = {}
with open(original_file, 'r') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        try:
            parts = line.split()
            if len(parts) < 2: continue
            wl = float(parts[0]) # Angstroms
            flux = float(parts[1])
            # Guardamos algunos puntos para verificar
            orig_data[wl] = flux
            if len(orig_data) > 100: break 
        except: continue

# Leer datos procesados y comparar
print("Leyendo archivo procesado y comparando...")
print(f"{'WL Orig (A)':<12} {'WL Proc (nm)':<12} {'Flux Orig':<12} {'Flux Proc':<12} {'Ratio Calc':<12} {'Ratio Esp':<12} {'Diff %':<8}")

count = 0
with open(processed_file, 'r') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        # Skip header line if present (Wavelength Flux)
        if 'Wavelength' in line: continue
        
        try:
            parts = line.split()
            wl_proc = float(parts[0]) # nm
            flux_proc = float(parts[1])

            # Revertir WL a Angstroms para buscar en el original
            wl_orig_equiv = wl_proc * 10.0

            # Buscamos si existe (con pequeña tolerancia)
            found_flux_orig = None
            for wl_o, flux_o in orig_data.items():
                if abs(wl_o - wl_orig_equiv) < 0.001:
                    found_flux_orig = flux_o
                    break

            if found_flux_orig is not None:
                ratio = flux_proc / found_flux_orig
                diff_percent = abs((ratio - total_expected_factor) / total_expected_factor) * 100

                print(f"{wl_orig_equiv:<12.4f} {wl_proc:<12.4f} {found_flux_orig:<12.4e} {flux_proc:<12.4e} {ratio:<12.4e} {total_expected_factor:<12.4e} {diff_percent:<8.4f}")
                count += 1
                if count >= 10: break
        except ValueError: continue

if count == 0:
    print("No se encontraron coincidencias exactas en las primeras líneas.")
else:
    print("\nConclusión:")
    print("Si 'Diff %' es cercano a 0, la conversión es matemáticamente correcta.")