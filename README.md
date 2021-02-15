### Testing tips

View [the presentation here](https://mitches-got-glitches.github.io/testing-tips/).


##### Parametrisation examples

This repo contains a number of different use cases for parametrising tests as outlined below. For the more complicated ones, they have been committed in several stages so that you're able to view the diffs and make sense of why parametrisation may be beneficial to use in your own tests. Each commit message explains the thinking behind each change. My advice would be to get comfortable with writing normal tests first, before beginning to think about parametrisation.

1. [Simple parametrisation](https://github.com/mitches-got-glitches/testing-tips/blob/master/test/simple_parametrisation.py)
2. Parametrising multiple parameters using [parametrize_cases](https://github.com/ckp95/pytest-parametrize-cases)
  a. [Stage 1](3e25b2b01bfbe5977f7eeeebeb968842a48cd6fa)
  b. [Stage 2](12113a3d23825f1194d0d5a02e0377b6db6717d2)
  c. [Stage 3](a288b6e0d2cb689999927145f1d8d547cd681187)
3. Parametrising a variable number of parameters by making use of kwargs
  a. [Stage 1](c44ffd8e301fec8ca652f273d01d043e3f2fd9b1)
  b. [Stage 2](2a6fa565458128294936d28d904fa0a5bdb829e4)
4. [Using fixtures in parametrisation](2a6fa565458128294936d28d904fa0a5bdb829e4)
5. Parametrising test cases using slices of dataframes
  a. [Stage 1](104e6844096bd72c6e72952098d2dc91b05be473)
  b. [Stage 2](dcb01dab4c18b994a7be372116f041b1224adf1e)
  c. [Stage 3](23bb85127d2cfe4e8c2177c8c6746f5f169fd3f0)