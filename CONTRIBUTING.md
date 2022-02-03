# Contributing to TransBigData

Whether you are a novice or experienced software developer, all contributions and suggestions are welcome!

## Getting Started

If you are looking to contribute to the *TransBigData* codebase, the best place to start is the [GitHub &#34;issues&#34; tab](https://github.com/ni1o1/transbigdata/issues). This is also a great place for filing bug reports and making suggestions for ways in which we can improve the code and documentation.

## Step-by-step Instructions of Contribute

The code is hosted on [GitHub](https://github.com/ni1o1/transbigdata),
so you will need to use [Git](http://git-scm.com/) to clone the project and make
changes to the codebase. 

1. Fork the [TransBigData repository](https://github.com/ni1o1/transbigdata).
2. Create a new branch from the `TransBigData` master branch.
3. Within your forked copy, the source code of `TransBigData` is located at the [src](https://github.com/ni1o1/transbigdata/tree/main/src) folder, you can make and test changes in the source code.
4. Before submitting your changes for review, make sure to check that your changes do not break any tests by running: ``pytest``. The tests are located in the [tests](https://github.com/ni1o1/transbigdata/tree/main/src/transbigdata/tests) folder.
5. When you are ready to submit your contribution, raise the Pull Request(PR). Once you finished your PR, the github [testing workflow](https://github.com/ni1o1/transbigdata/actions/workflows/tests.yml) will test your code. We will review your changes, and might ask you to make additional changes before it is finally ready to merge. However, once it's ready, we will merge it, and you will have successfully contributed to the codebase!

# 为TransBigData贡献代码

无论您是新手还是经验丰富的软件开发人员，欢迎您提供所有意见和建议！

## 开始

如果你想为*TransBigData*代码库做贡献，最好从[GitHub issues](https://github.com/ni1o1/transbigdata/issues)开始。你可以在这里提交BUG报告，并提出改进代码和文档的方法和建议。

## 如何贡献代码

代码托管在[GitHub](https://github.com/ni1o1/transbigdata)，所以你需要使用[Git](http://git-scm.com/)克隆项目并对代码做出更改。具体方法如下：
1. Fork [`TransBigData`仓库](https://github.com/ni1o1/transbigdata).
2. 以`TransBigData`的`main`分支为基础创建新分支。
3. 在您的分支仓库中，`TransBigData`的源代码位于[src](https://github.com/ni1o1/transbigdata/tree/main/src)文件夹，您可以在源代码中进行和测试更改，如果你使用的是jupyter notebook,可以在src文件夹下建立ipynb文件进行调试，这样修改transbigdata的源码时可以直接读取到。
4. 在提交更改以供审阅之前，请运行`pytest`来测试代码，确保您对代码的更改不会破坏任何测试结果。测试代码位于[tests](https://github.com/ni1o1/transbigdata/tree/main/src/transbigdata/tests)文件夹中
5. 当你准备好提交你的贡献时，提交Pull Request（PR）。完成PR后，github提供的[测试工作流](https://github.com/ni1o1/transbigdata/actions/workflows/tests.yml)将测试您的代码，并将测试结果做出分析。
6. test分两部分，一部分是旧的代码会test保证输出一致，另一部分是你增加的方法需要自己写个test文件，增加test，这样后面贡献的人要改你代码时也会test，确保不会更变你的程序功能。`TransBigData`的测试结果在[![codecov](https://codecov.io/gh/ni1o1/transbigdata/branch/main/graph/badge.svg?token=GLAVYYCD9L)](https://codecov.io/gh/ni1o1/transbigdata)这里可以看到，其中的百分比表示单元测试覆盖率，表明有多少比例的代码通过了测试。
7. 测试成功后，我们将检查您的更改，并可能要求您在最终准备合并之前进行其他更改。如果成功，我们将merge到`main`分支中，贡献就成功啦。

## 如何贡献代码的视频介绍
[bilibili](https://www.bilibili.com/video/BV1K44y1H7ML/)
[Youtube](https://www.youtube.com/watch?v=ocjzT-23pak)
