[![BuildStatus](https://travis-ci.org/undefinedvalue/lucidblue.svg)](https://travis-ci.org/undefinedvalue/lucidblue)

# lucidBlue
https://lucidblue.net

lucidBlue is a personal website. It consists of website content and the
tools used to develop and deploy it.

* [License](#license)
* [Build and Development](#build-and-development)
 * [Build](#build)
 * [Development Server](#development-server)
* [Build Pipeline Details](#build-pipeline-details)
 * [1. Compile Jinja Templates](#1-compile-jinja-templates)
 * [2. Compile Sass Templates](#2-compile-sass-templates)
 * [3. Upload to S3](#3-upload-to-s3)


## License
The lucidBlue website content is made available under the [CC BY
License](https://creativecommons.org/licenses/by/4.0/). This includes any
content found on the live [lucidBlue](https://lucidblue.net) website, and
excludes the other offline components that are in this repository, which are
licensed under the [MIT License](https://opensource.org/licenses/MIT).

Linking to https://lucidblue.net or this GitHub repository is sufficient
attribution.


## Build and Development
The primary build tool is found in [dev/build.py](dev/build.py).

```bash
cd lucidblue
./dev/build.py -h
```

### Build
Building the website takes the source files in the [www][www] directory,
processes them, then outputs the final website files to a temporary
directory called "build".

Building involves running the build pipeline, which is defined by python
scripts in the [dev/build_pipeline](dev/build_pipeline) directory.
Scripts are run in alphabetical order of file name, which is why they are
prefixed with numbers. Lower numbers run first.

```bash
cd lucidblue
./dev/build.py build
```

Sometimes it is useful to skip certain steps of the build:

```bash
./dev/build.py build --skip s3_upload
```

### Development Server
The development server is useful to run when editing the source files so that
changes can be previewed immediately on the current machine.

The development server runs on localhost:8080 and serves the website from the
local build directory. It also watches for changes in source files and
rebuilds the website when changes occur. Combined with a [special javascript
file](dev/workflow/refresh.js) that is only loaded when running on the
development server, the website will automatically reload with the newly built
version whenever source files are edited.

```bash
cd lucidblue
./dev/build.py server
```

Sometimes it is useful to disable the auto-reload javascript. To do so, add a
query parameter "refresh=false": http://localhost:8080?refresh=false

If changes are made to the development tools themselves, the development server
will need to be stopped and restarted before it sees those changes.


## Build Pipeline Details
The build pipline is composed of multiple steps. Each step outputs a new directory
of files. The input to each step is the output directory of the previous step,
except for the first step which uses the www directory.

### 1. Compile Jinja Templates
Pipeline script: [100_compile_templates.py](dev/build_pipeline/100_compile_templates.py)

This step compiles all [Jinja2](http://jinja.pocoo.org/) templates. The templates are files
that have a ".j2" extension.

Jinja templates are used here to reduce repetition in source code and help break
apart pieces of the website into logical chunks.

### 2. Compile Sass Templates
Pipeline script: [110_compile_sass.py](dev/build_pipeline/110_compile_sass.py)

This step compiles all [Sass](http://sass-lang.com) templates. The templates are files that
have a ".scss" extension.

Sass templates are used to make writing CSS much easier and cleaner.

### 3. Upload to S3
Pipeline script: [200_s3_upload.py](dev/build_pipeline/200_s3_upload.py)

This step uploads the final build directory to [S3](https://aws.amazon.com/s3/).
In effect, this deploys the website.
