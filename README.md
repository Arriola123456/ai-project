# La brecha de participación a los 70 años sobrestima el efecto del voto obligatorio

**Manuel Alfredo Arriola Montenegro** · Inteligencia Artificial y Modelamiento Económico · UP 2026-II

*Track B: el modelo económico detrás de mi tesis sobre el voto facultativo desde los 70 años.*

## La pregunta y el resultado

En el Perú el voto es obligatorio de 18 a 69 años y facultativo desde los 70. La ONPE reporta una
caída de 25 a 46 puntos entre los grupos de 60–69 y 70+, pero la edad viene en intervalos y el
último es abierto. **Resultado:** la brecha $\Delta$ es una cota superior del efecto causal
$\tau^{70}$ si la participación, hábito incluido, no crece entre los 60 y los 70 años (Proposición 3).
Calibrado a seis elecciones presidenciales (2001–2026), $\tau^{70}$ es solo el 18–22% de la brecha;
el resto es envejecimiento dentro de la banda 70+.

## El modelo

El ciudadano $i$ de edad $a$ vota si y solo si
$\varepsilon_{it} < b(a) + \lambda h_{it} + O_a S_t - \mu_t - \eta_i$, con $O_a = \mathbb 1[a<70]$,

- beneficio por edad $b(a) = A a^{\alpha} - \kappa a^{\beta}$, con $0<\alpha<1\le\beta$;
- hábito autorregresivo $h_{i,t+1} = \rho(a_{it})\,h_{it} + v_{it}$, cuyo shock es el voto anterior;
- sanción $S_t = s_0 + q F_t \ge 0$, con $F_t$ la multa en % de la UIT; elecciones cada $d=5$ años.

Resultados: Lema 1 (acoplamiento), P1 (ciclo de vida y edad de máximo $a^*$), P2 (el salto no
contiene hábito), P3 (cota superior bajo (H)), P4 (escalones del hábito cada 5 años, identidad
exacta) y P5 (persistencia creciente: la identidad gana un resto $R(a)\ge0$).

## Estado (31-oct-2026)

| Componente | Estado |
|---|---|
| Tema (`proposal/`, `slides/topic.*`) | Presentado el 7-oct-2026 |
| Slides finales (`slides/final.*`) | 41 slides más 2 de respaldo, para el miércoles 4-nov-2026 (08:20): el modelo se arma en seis pasos, con gráficos de `code/slide_figures.py`; resultado central: los escalones de la costumbre (P3) |
| Paper (`paper/`) | Borrador completo (modelo, pruebas, calibración, apéndices); versión final el 26-nov |
| Simulaciones (`python3 code/verify.py`) | Comprueba P1–P5, los contraejemplos y reproduce la calibración |
| Calibración (`code/calibrate.py`) | Modelos M0–M3 en `code/output/`; datos agregados en `code/data/` |
| Lean (`lean/`) | Lema 1 y P1–P5 probados, sin `sorry`; ver el apéndice A del paper |
| Apéndice a mano (`hand/`) | `hand/01-derivacion-del-modelo.pdf`: del planteamiento a la costumbre promedio $H(a)$; falta el resto $R(a)$ y la versión final para el paper |
| `prompts.md` | Al día |

Los momentos de `code/data/` son agregados (perfiles por edad, niveles por banda, electores por edad
y multa media) derivados de los resultados de la tesis; no hay microdatos en este repositorio.

## Reproducir

```bash
python3 -m pip install -r code/requirements.txt
python3 code/verify.py            # checks + tablas, figuras y cifras del texto (~3 min)
python3 code/slide_figures.py     # solo las figuras de las slides (verify.py ya lo llama)
python3 code/calibrate.py         # recalibra M0-M3 (lento); --full para la robustez
cd paper  && latexmk -pdf paper.tex
cd slides && latexmk -pdf final.tex
```

El workflow de `.github/workflows/build.yml` recompila los PDFs y corre `code/verify.py` en cada
push.
