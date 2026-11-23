# Voto obligatorio a los 70 años: el salto, la edad y la costumbre de votar

**Manuel Alfredo Arriola Montenegro** · Inteligencia Artificial y Modelamiento Económico · UP 2026-II

*Track B: el modelo económico detrás de mi tesis sobre el voto facultativo desde los 70 años.*

## La pregunta y el resultado

En el Perú el voto es obligatorio de 18 a 69 años y facultativo desde los 70. Con datos por edad
exacta, la participación cae entre 5 y 12 puntos en el umbral y después sigue cayendo. **Pregunta:**
¿esa caída posterior es la edad o la costumbre de votar que se pierde sin obligación?
**Resultado central (Proposición 3):** si votar crea hábito ($\lambda>0$), con elecciones cada
$d=5$ años y un entorno estacionario, el hábito medio cae en **escalones** a los 75, 80 y 85 años, y el
primer escalón repite el salto de los 70; sin hábito no hay escalones. En los perfiles por edad
exacta de la tesis, la caída en 74→75 y en 79→80 supera a la de las demás edades en 5 de 6 elecciones.

## El modelo

El ciudadano $i$ de edad $a$ vota si y solo si
$\varepsilon_{it} < b(a) + \lambda h_{it} + O_a S_t - \mu_t - \eta_i$, con $O_a = \mathbb 1[a<70]$,

- beneficio por edad $b(a) = A a^{\alpha} - \kappa a^{\beta}$, con $0<\alpha<1\le\beta$;
- hábito $h_{i,t+1} = \rho(a_{it})\,h_{it} + v_{it}$, cuyo shock es el voto anterior;
- sanción $S_t = s_0 + q F_t \ge 0$, con $F_t$ la multa en % de la UIT.

Resultados: Lema 1 (acoplamiento), P1 (ciclo de vida, máximo en $a^*$), P2 (el salto no contiene
hábito y el hábito lo achica), **P3 (escalones)**, P4 (persistencia creciente: resto $R(a)\ge0$) y una
observación sobre la heterogeneidad (signo de $\partial\tau^{70}/\partial s$ cuando la mayoría vota).

## Estado (23-nov-2026)

| Componente | Estado |
|---|---|
| Tema (`proposal/`, `slides/topic.*`) | Presentado el 7-oct-2026 |
| Presentación final (`slides/final.*`) | Presentada el 4-nov-2026 |
| Paper (`paper/`) | Versión final: unas 10,5 páginas de cuerpo, pruebas completas, calibración y apéndices |
| Simulaciones (`python3 code/verify.py`) | Comprueba P1–P4, la observación de heterogeneidad, la calibración y los escalones en los datos |
| Calibración (`code/calibrate.py`) | Modelos M0–M3 en `code/output/`; datos agregados en `code/data/` |
| Lean (`lean/`) | `Arriola26VotingHabit` sobre el paper final (`7fa3a62`): Lema 1, P1–P4 y la Observación 1 probados, sin `sorry`; *formalized with caveat* (hecha por Claude Code) |
| Apéndice a mano (`hand/`) | `01-derivacion-del-modelo.pdf`, hasta $H(a)$; **pendiente completarlo** (P2, escalones, $R(a)$, heterogeneidad) |
| `prompts.md` | Al día |

Los datos de `code/data/` son agregados derivados de la tesis (perfiles por edad, niveles por banda,
electores por edad y multa media); no hay microdatos en el repositorio.

## Reproducir

```bash
python3 -m pip install -r code/requirements.txt
python3 code/verify.py            # checks, tablas, figuras y cifras del texto (~3 min)
python3 code/calibrate.py         # recalibra M0-M3 (lento); --full para la robustez
cd paper  && latexmk -pdf paper.tex
cd slides && latexmk -pdf final.tex
```

El workflow `.github/workflows/build.yml` recompila los PDFs y corre `code/verify.py` en cada push.
