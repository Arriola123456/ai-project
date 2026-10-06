# Voto obligatorio, envejecimiento y la brecha de participación a los 70 años

**Manuel Alfredo Arriola Montenegro** · Inteligencia Artificial y Modelamiento Económico · UP 2026-II

*Track B: el modelo económico detrás de mi tesis.*

## La pregunta

En el Perú el voto es obligatorio de 18 a 69 años y facultativo desde los 70. La ONPE
muestra una caída grande y recurrente de la participación entre los grupos de 60–69 y 70+
(2001–2026), pero reporta la edad solo en intervalos y el grupo 70+ es abierto. ¿Qué mide
esa brecha observada, y cómo responde a la multa por omisión (Ley 28859)?

## El modelo

Cálculo del voto con obligatoriedad (Riker y Ordeshook, 1968; Panagopoulos, 2008), con
beneficio dependiente de la edad y del hábito. El ciudadano de edad $a$ elige
$v\in\{0,1\}$:

$$\max_{v\in\{0,1\}}\; v\,[B(a,h)-c] + (1-v)\,[-O\,S],\qquad O=\mathbb 1[a<70],\; S=qF,$$

con costo $c\sim G$ (continua, estrictamente creciente, la misma a toda edad). Vota si y solo si
$c<c^*(a)\equiv B(a,h)+O\,S$, así que $P_1(a)=G(B+S)$ y $P_0(a)=G(B)$.

## El resultado principal, con todas sus condiciones

El efecto causal en el umbral es la masa de *compliers*,
$\tau^{70}=G(c_1)-G(c_0)$ con $c_0=B(70,h)$ y $c_1=c_0+S$ ($B$ continuo en 70). Lo que
identifican los datos por grupo es
$\Delta=\mathbb E_{[60,70)}[P_1(a)]-\mathbb E_{a\ge70}[P_0(a)]$.

**Conjetura central (i):** si el hábito es común ($h=\bar h$) y $B$ es no creciente en la edad
desde los 60, entonces $\Delta\ge\tau^{70}>0$: la brecha observada es una cota superior del
efecto de la obligatoriedad. Además $\partial\Delta/\partial S=\mathbb E_{[60,70)}[g(c^*(a))]>0$,
con rendimientos decrecientes si los cortes de los obligados están por encima de la moda, y
$\partial\Delta/\partial s<0$ si $G$ es simétrica de dispersión $s$ y
$P_0(70)\le 50\%<P_1(70^-)$ **en el umbral**. Con promedios por grupo esto último es
falso; el contraejemplo está en la propuesta.

## Estado

| Componente | Estado |
|---|---|
| Documento de tema y slides (`proposal/`, `slides/topic.*`) | Listos para la presentación del 7-oct-2026 (08:45) |
| Slides finales (`slides/final.*`) | Pendiente (presentación 30-oct-2026); aún es la plantilla |
| Paper (`paper/`) | Pendiente (26-nov-2026); aún es la plantilla |
| Simulaciones (`python3 code/verify.py`) | Pendiente; aún corre el modelo de juguete de la plantilla |
| Lean (`check --fast`, commit del paper formalizado) | Pendiente; se corre sobre el paper |
| Apéndice a mano (`hand/`) | Pendiente |
| `prompts.md` | En curso |

## Compilación

```bash
python3 -m pip install -r code/requirements.txt && python3 code/verify.py
cd proposal && latexmk -pdf proposal.tex
cd slides   && latexmk -pdf topic.tex final.tex
cd paper    && latexmk -pdf paper.tex
```

El workflow de `.github/workflows/build.yml` recompila los PDFs y corre `code/verify.py` en
cada push.
