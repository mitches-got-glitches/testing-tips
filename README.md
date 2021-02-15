# Testing Tips

View [the presentation here](https://mitches-got-glitches.github.io/testing-tips/).


## Parametrisation examples

This repo contains a number of different use cases for parametrising tests as outlined below. For the more complicated ones, they have been committed in several stages so that you're able to view the diffs and make sense of why parametrisation may be beneficial to use in your own tests. Each commit message explains the thinking behind each change. My advice would be to get comfortable with writing normal tests first, before beginning to think about parametrisation.

1. [Simple parametrisation](test/simple_parametrisation.py)
2. Parametrising multiple parameters using [parametrize_cases](https://github.com/ckp95/pytest-parametrize-cases)
    - [Stage 1](3e25b2b01bfbe5977f7eeeebeb968842a48cd6fa)
    - [Stage 2](12113a3d23825f1194d0d5a02e0377b6db6717d2)
    - [Stage 3](a288b6e0d2cb689999927145f1d8d547cd681187)
3. Parametrising a variable number of parameters by making use of kwargs
    - [Stage 1](c44ffd8e301fec8ca652f273d01d043e3f2fd9b1)
    - [Stage 2](2a6fa565458128294936d28d904fa0a5bdb829e4)
4. [Using fixtures in parametrisation](2a6fa565458128294936d28d904fa0a5bdb829e4)
5. Parametrising test cases using slices of dataframes
    - [Stage 1](104e6844096bd72c6e72952098d2dc91b05be473)
    - [Stage 2](dcb01dab4c18b994a7be372116f041b1224adf1e)
    - [Stage 3](23bb85127d2cfe4e8c2177c8c6746f5f169fd3f0)


## VS Code Snippets

I've included a [JSON file](python_test_snippets.json) that contains many of the Python snippets I've written to help me with testing. Feel free to copy and adjust to your liking. To add snippets in VS Code, press CTRL + SHIFT + P to open the command palette, type "snippet" and select "Configure User Snippets" which will open the JSON of Python snippets for your user profile. Simply copy the snippets you want across.

A demo on how these work will be added to the presentation in due course.