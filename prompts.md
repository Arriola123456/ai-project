# Prompts

Mis prompts y las respuestas relevantes, en crudo. Las verificaciones están marcadas con
**Verificación**; los veredictos irán al apéndice *AI collaboration log* del paper.

---

## Sesión 1 — claude.ai (Claude Opus 5.5), hasta el 6-oct-2026: borrador del documento de tema y del deck

> **Pendiente:** pegar aquí la exportación de la conversación en la que se redactaron
> `topic_doc.tex` y `topic_presentation.tex` (estructura, modelo, Proposiciones esperadas
> (a)–(d) y (i)–(iv), diagramas TikZ).

---

## Sesión 2 — Claude Code (Claude Opus 5.5), 6-oct-2026: armar el repositorio y revisar el tema

### Turno 1

**Prompt**

```text
Revisa la tarea que me han dejado para mi curso de IA y Modelamiento Económico:

https://github.com/alexanderquispe/AI-Econ-Modeling/issues/7

ya he avanzado con el doc y la topic presentation, los puedes encontrar en la siguiente dirección:

C:\Users\manue\OneDrive\Escritorio\IA_Econ_Model_PP

ya cree el repositorio de la plantilla solicitada (actualmente es igual a la plantilla). Ayudame a terminar la tarea trabajando en mi github. El link de mi repositorio es este:

https://github.com/Arriola123456/ai-project

+ultrathink
```

**Respuesta (resumen de lo que hizo el agente)**

- Leyó el issue #7 y `PRESENTATIONS.md`: mi presentación de tema es el miércoles 7-oct
  a las 08:45 (sesión 13), así que el documento y las slides deben estar en `main` antes de
  las 07:30.
- Comparó los PDFs con lo que pide el issue. Faltaban el enlace al repositorio en la portada,
  la sección *Plan y riesgos* (qué probar, simular y formalizar en Lean, y el paso con más
  riesgo) y el detalle de dónde se buscó la literatura. El deck citaba "H3" sin definirla.
- Revisó las citas contra fuentes primarias. Gonzales, León-Ciliotta y Martínez (2022)
  explotan la exención de los 70: en las diapositivas de la AEA 2020, "Turnout falls 20 pp
  between ages 69 and 72 (< 2 pp in Chile)" y "A 100% reduction of the fine has < 1/5 the
  effect of CV exemption". Cepaluni y Hidalgo (2016) usan "two age-based discontinuities"
  en Brasil. Para Jaitman (2013) no se pudo confirmar el umbral desde la fuente, así que se
  dejó como "umbrales de edad".

**Verificación (script en SymPy y NumPy, normal como $F$)**

```text
(a)-(d) symbolic formulas OK
(d) sign OK on 1e5 draws
group averages: P1=0.579 (>0.5), P0=0.0013 (<=0.5); s*dDelta/ds = +0.1010
=> (iv) with group-average conditions is FALSE; needs P1(70-) > 1/2 >= P0(70)
(i) Delta >= tau70 > 0 OK on 2000 random profiles
```

**Qué hice con ello:** acepté la corrección de (iv). La condición ahora va en el umbral,
$P_0(70)\le 50\% < P_1(70^-)$, y con $B$ no creciente vale para cada edad de ambos grupos;
también saqué la unimodalidad, que sobraba. El contraejemplo quedó en el documento y en una
slide. El agente señaló además que, como $P_0(70)\ge\mathbb E_{a\ge70}[P_0(a)]$, la condición
de (d) falla en 2006, 2011 y 2016 (70+ sobre 50% en el gráfico de la ONPE). Lo puse como el
riesgo principal.

### Turno 2

**Prompt**

```text
Ya te dejé el topic doc y el topic presentation como .tex en la carpeta, usalos
```

**Respuesta (resumen)**

Descartó su reconstrucción desde los PDFs y usó mis `.tex` como base, con cambios puntuales:
el enlace al repositorio (portada y cierre), la corrección de (iv) y su contraejemplo, la
precisión sobre Gonzales et al. y Jaitman/Cepaluni-Hidalgo, "Dónde busqué", la sección
*Plan y riesgos* (documento) y las slides de plan con Lean y del paso con más riesgo (deck).
Escribió también el README.
