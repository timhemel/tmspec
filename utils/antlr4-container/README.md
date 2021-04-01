# Building the ANTLR container

First, check out the ANTLR source code. In this README, I assume you are in the `utils/antlr4-container` directory.
Since we want to build version 4.9.1, I check out that release.

```
$ git clone https://github.com/antlr/antlr4.git
$ cd antlr4
$ git checkout 4.9.1
$ cd ..
```

Now, build the container. I am using [Podman](https://podman.io/), but you can replace `podman` with `docker` if you are using Docker. For Docker,
you may need to use the option `-f Containerfile`.

```
$ podman image build -t antlr4:4.9.1 .
```

# Running the ANTLR4 container

Copy the scripts `antlr4` and `grun` into a directory that is in your `$PATH`. If you don't use Podman, but Docker, replace `podman` with `docker`.
Note that because the scripts map the current working directory under `/work`, they can only work with relative paths and only with files that are
in or below the current working directory.

The script `javac` will run the Java compiler from the ANTLR container. It works just like the other scripts.


