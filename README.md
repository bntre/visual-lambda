<sub>The project was migrated from https://code.google.com/archive/p/visual-lambda/ and from https://bitbucket.org/bntr/visual-lambda.</sub>

# Visual Lambda Calculus

![logo](https://bntr.planet.ee/lambda/loop_.gif)

Visual Lambda is a graphical environment and visual programming tool
for exploring untyped lambda calculus using Bubble Notation.  
It represents lambda expressions as colorful, tree-like 2D structures
and animates beta-reduction smoothly, making reductions easy to follow.

The project started as a master's thesis (2008); see the thesis for details:
[visual_lambda.pdf](https://bntr.planet.ee/lambda/work/visual_lambda.pdf).

This might be useful for students, educators and researchers who want
an intuitive, interactive way to explore λ‑calculus and reduction strategies.

**Try it live**: https://bntre.github.io/visual-lambda/

Lambda puzzles **challenge**: https://bntre.github.io/visual-lambda/#workspace=puzzles

<sub>Or alternatively: https://bntr.itch.io/visual-lambda</sub>

![Screenshot](https://raw.githubusercontent.com/bntre/visual-lambda/master/res/screenshot.png)


## Bubble Notation

![Basics](https://bntr.planet.ee/lambda/visual_lambda_bubble_notation.gif)

Watch a short demo to get an idea of how Bubble Notation works:  
https://www.youtube.com/watch?v=aRgu8S3Pnb8

<p><a href="https://www.youtube.com/watch?v=aRgu8S3Pnb8" title="Factorial 3">
 <img src="https://img.youtube.com/vi/aRgu8S3Pnb8/maxresdefault.jpg" width="600" alt="Factorial 3"/>
</a></p>

Other video examples:
- Pairs, construction and reduction: https://www.youtube.com/watch?v=YEyyyzUuUJQ
- Predecessors: https://www.youtube.com/watch?v=CWzn2ucPMdg
- Recursion: https://www.youtube.com/watch?v=bGG9exO2kew

Old GIF examples:
- 'MULT 3 2' evaluation: [MULT_3_2_=_6.gif](https://bntr.planet.ee/lambda/visual_lambda_MULT_3_2_=_6.gif)
- 'Y I' evaluation: [Y_I.gif](https://bntr.planet.ee/lambda/Y_I.gif)


## Local run

Dependencies
- Python 3.8+
- pygame-ce 2.5.6

```
pip install pygame-ce==2.5.6
python main.py
```

## Controls

See the full UI control reference in [controls.txt](controls.txt).

## Expression library

The repository includes a small library of predefined expressions that
you can paste into the console: see [library.txt](library.txt).

## Related work

- [Programming with Visual Expressions, Wayne Citrin](https://web.archive.org/web/20110524135539/users.encs.concordia.ca/~haarslev/vl95www/html-papers/citrin/citrin.html)
- [A Graphical Notation for the Lambda Calculus, Dave Keenan](https://dkeenan.com/Lambda/)
- [Alligator Eggs, Bret Victor](http://worrydream.com/AlligatorEggs/) ([browser game](https://tibordp.github.io/gator-calculus/))
- More in [Prathyvsh's catalog](https://github.com/prathyvsh/lambda-calculus-visualizations)

## Future work

I still think Bubble Notation is a promising way to represent lambda terms, but this implementation is a bit dated.  
A modern reimplementation could improve interaction and visuals.  
Possible directions:

- Make terms feel more "springy" and react to dragging with natural, physics-like motion.
- Revisit the lazy-evaluation visualization to make it clearer and more robust.

## License
- Visual Lambda is licensed under the GNU Lesser General Public License v3.0.
- This project also includes Open Sans, licensed under the SIL Open Font License 1.1.
