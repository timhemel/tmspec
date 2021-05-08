# Containerized build tools

You may not want to install build tools on your main system, but run them in containers,
to keep things clean. Usually this works ok, but there are some caveats.

## antlr4

The `utils` directory in the source tree contains a `Containerfile` to build ANTLR. Follow the instructions in the README to build it.
There are two scripts: `antrl4` and `grun`, that you can put into your `$PATH`. Note that because it maps the current working directory under `/work`, it can only work with relative paths and only with files that are in or below the current working directory. The `build.sh` script in `src/tmspec` takes this into account.

To run the Java compiler, you can also use the ANTLR container. Just copy the script `javac` to your `$PATH`.

# Testing the grammar

To test the grammar, you can use ANTLR's test tool (https://github.com/antlr/antlr4/blob/master/doc/getting-started.md).

Copy the grammar to a separate directory, to not clutter the tmspec source directory:

```
$ mkdir grammar-test
$ cp src/tmspec/tmspec.g4 grammar-test
```

Then, create parsers for java and compile them:

```
$ cd grammar-test
$ antlr4 -Dlanguage=Java tmspec.g4
$ javac -cp /usr/local/lib/antlr4-tool.jar tmspec*.java
```

Since the default target language is Java, you can omit `-Dlanguage=java` from the command.

Now you can run the test tool. `grun` is an alias that calls the test tool, as described in the
[ANTLR getting started page](https://github.com/antlr/antlr4/blob/master/doc/getting-started.md).

```
$ grun tmspec start inputfile -tokens
$ grun tmspec start inputfile -tree
```


