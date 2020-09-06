# calc2tex

Computing values of formulas and displaying them in LaTeX.

## Quickstart

For a complete documentation see the [docs](https://github.com/stbech/calc2tex/).

### Requirements

* Python: 3.6+
* LaTeX-packages: `siunitx, booktabs, amsmath`

### Install

```none
pip install calc2tex
```

### Example

Create a `input.txt`-file containing:

```txt
x; x_i; 12; m
y; y_{res};; x**2*3; m**2
```

Create a `start.tex`-file which includes:

```latex
in = Calc2tex("input.txt", "EN")
in.table()
Some text.
$$in.comp("y")$$
```

After running following python-script:

```python
import calc2tex
calc2tex.process_tex("start.tex", "output.tex")
```

a new file `output.tex` is created which contains:

```latex

\begin{table}[htbp]
    \centering
    \caption{input values}
    \label{tab:input_val}
    \begin{tabular}{lcc}
        \toprule
        variable & value & unit\\
        \midrule
        $x_i$ & 12.0 & $\si{\meter}$\\ 
        \bottomrule
    \end{tabular}
\end{table}
Some text.
$$y_{res} =& x_i^{2}\cdot 3 = \SI{12.0}{\meter}^{2}\cdot 3 = \SI{432.0}{\meter\tothe{2}}$$
```

## Issues

* calc2tex is currently in development, so changes will happen in the future.
* `a/b/c` will not be evaluated correctly, use: `a/(b*c)`

## License

calc2tex is released under the MIT license.
