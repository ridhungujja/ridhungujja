<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img alt="Ridhun Gujja — empirical finance, econometrics, python. High school student and econometrics intern in Wilmington, DE." src="assets/banner-light.svg" width="880">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/ridhungujja/ridhungujja/clock-output/clock-dark.svg">
  <img alt="Local time in Wilmington, DE" src="https://raw.githubusercontent.com/ridhungujja/ridhungujja/clock-output/clock-light.svg" width="220">
</picture>

I'm a high school student working on empirical finance questions — mostly the kind
where the interesting part is the identification, not the model. I write Python for
research and TypeScript for the things I wish existed.

## Currently

- Building **[Podium](https://github.com/ridhungujja/podium)** — instant judge-style feedback on extemp speeches
- Finishing the writeup for **[PE Firm Persistence](https://github.com/ridhungujja/pe-firm-persistence)**, on whether private equity returns carry across funds
- Running my **ISEF project**: a 4×5 factorial study of whether *how a prompt is phrased* — neutral, urgent, authority-appealing, or emotionally loaded — changes how often a language model hallucinates, holding the actual question constant across five models with different alignment regimes
- Open to research assistant work in empirical finance or econometrics

## Selected work

### [PE Firm Persistence](https://github.com/ridhungujja/pe-firm-persistence) · Python

Do good private equity funds predict good successors? Pension funds allocate billions
on the assumption that they do. I test it on CalPERS' legally-mandated quarterly
disclosures — 462 published rows down to 65 mature, adjacent fund pairs — regressing
log TVPI on the predecessor fund's, with vintage fixed effects and errors clustered
on the fund family.

```
β = 0.214    SE 0.138    95% CI [−0.057, 0.485]
p = 0.121    wild cluster bootstrap p = 0.187    n = 65
```

The interval contains zero. On this data, persistence can't be told apart from luck —
and the sample dies at 65 pairs for reasons worth more than the coefficient.

### [Forma](https://github.com/ridhungujja/forma) · JavaScript

A Chrome extension that restructures PDFs, DOCX and slide decks into clean Markdown
*before* they upload to Claude. Claude's native PDF pipeline renders every page as an
image as well as extracting its text, so a large share of the token cost is a vision
tax that a clean text upload never pays. Forma removes it locally — no document
content ever leaves the browser tab.

### [Podium](https://github.com/ridhungujja/podium) · TypeScript

Draw a question, prep, speak, get structured feedback on structure, content and
delivery in under a minute. Built for high school extempers without a coach.
Next.js 14 · Tailwind · Framer Motion.

## Stack

**Languages**

<a href="https://www.python.org" title="Python"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/python-dark.svg"><img src="assets/tiles/python-light.svg" height="48" alt="Python"></picture></a><a href="https://www.r-project.org" title="R"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/r-dark.svg"><img src="assets/tiles/r-light.svg" height="48" alt="R"></picture></a><a href="https://www.postgresql.org" title="SQL"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/sql-dark.svg"><img src="assets/tiles/sql-light.svg" height="48" alt="SQL"></picture></a><a href="https://www.latex-project.org" title="LaTeX"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/latex-dark.svg"><img src="assets/tiles/latex-light.svg" height="48" alt="LaTeX"></picture></a><a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript" title="JavaScript"><img src="assets/tiles/javascript-light.svg" height="48" alt="JavaScript"></a><a href="https://developer.mozilla.org/en-US/docs/Web/HTML" title="HTML"><img src="assets/tiles/html-light.svg" height="48" alt="HTML"></a><a href="https://developer.mozilla.org/en-US/docs/Web/CSS" title="CSS"><img src="assets/tiles/css-light.svg" height="48" alt="CSS"></a><a href="https://www.gnu.org/software/bash/" title="Bash"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/bash-dark.svg"><img src="assets/tiles/bash-light.svg" height="48" alt="Bash"></picture></a>

**Libraries**

<a href="https://pandas.pydata.org" title="pandas"><img src="assets/tiles/pandas-light.svg" height="48" alt="pandas"></a><a href="https://numpy.org" title="NumPy"><img src="assets/tiles/numpy-light.svg" height="48" alt="NumPy"></a><a href="https://www.statsmodels.org" title="statsmodels"><img src="assets/tiles/statsmodels-light.svg" height="48" alt="statsmodels"></a><a href="https://scipy.org" title="SciPy"><img src="assets/tiles/scipy-light.svg" height="48" alt="SciPy"></a><a href="https://matplotlib.org" title="Matplotlib"><img src="assets/tiles/matplotlib-light.svg" height="48" alt="Matplotlib"></a><a href="https://react.dev" title="React"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/react-dark.svg"><img src="assets/tiles/react-light.svg" height="48" alt="React"></picture></a><a href="https://nextjs.org" title="Next.js"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/next-js-dark.svg"><img src="assets/tiles/next-js-light.svg" height="48" alt="Next.js"></picture></a>

**Software &amp; Tools**

<a href="https://www.stata.com" title="Stata"><img src="assets/tiles/stata-light.svg" height="48" alt="Stata"></a><a href="https://git-scm.com" title="Git"><img src="assets/tiles/git-light.svg" height="48" alt="Git"></a><a href="https://github.com/ridhungujja" title="GitHub"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/github-dark.svg"><img src="assets/tiles/github-light.svg" height="48" alt="GitHub"></picture></a><a href="https://claude.com/claude-code" title="Claude Code"><img src="assets/tiles/claude-code-light.svg" height="48" alt="Claude Code"></a><a href="https://docs.pytest.org" title="pytest"><img src="assets/tiles/pytest-light.svg" height="48" alt="pytest"></a><a href="https://github.com/jsvine/pdfplumber" title="pdfplumber"><img src="assets/tiles/pdfplumber-light.svg" height="48" alt="pdfplumber"></a>

## By the numbers

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/activity-dark.svg">
  <img alt="Contributions, commits, projects and total code written in the past year." src="assets/activity-light.svg" width="880">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/langs-dark.svg">
  <img alt="Code by language across public projects." src="assets/langs-light.svg" width="880">
</picture>

## On repeat

<a href="https://open.spotify.com/track/1zzejMGRYKP5XOa3FmzXfa"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/spotify-1-dark.svg"><img alt="Katchi Sera by Sai Abhyankkar" src="assets/spotify-1-light.svg" width="416"></picture></a><a href="https://open.spotify.com/track/7H7NyZ3G075GqPx2evsfeb"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/spotify-2-dark.svg"><img alt="Chamber Of Reflection by Mac DeMarco" src="assets/spotify-2-light.svg" width="416"></picture></a>

<sub>Covers and titles pulled from Spotify · out of <a href="https://open.spotify.com/playlist/0v23S8pWmoUcxv1chc8kzh">cash curious 💰💸</a></sub>

## Elsewhere

<a href="mailto:ridhung@gmail.com" title="Gmail"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/gmail-dark.svg"><img src="assets/tiles/gmail-light.svg" height="48" alt="Gmail"></picture></a><a href="https://github.com/ridhungujja" title="GitHub"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/github-dark.svg"><img src="assets/tiles/github-light.svg" height="48" alt="GitHub"></picture></a><a href="https://www.linkedin.com/in/ridhungujja/" title="LinkedIn"><img src="assets/tiles/linkedin-light.svg" height="48" alt="LinkedIn"></a><a href="https://www.instagram.com/ridhungujja/" title="Instagram"><img src="assets/tiles/instagram-light.svg" height="48" alt="Instagram"></a><a href="https://open.spotify.com/playlist/0v23S8pWmoUcxv1chc8kzh" title="Spotify"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/tiles/spotify-dark.svg"><img src="assets/tiles/spotify-light.svg" height="48" alt="Spotify"></picture></a>

<a href="https://www.buymeacoffee.com/ridhungujja">
  <img alt="Pickleball + Eats" height="46" src="assets/bmc-button.svg">
</a>
