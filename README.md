<h1 align="center">matteosox/nba</h1>

## [Badges? We ain't got no badges! We don't need no badges! I don't have to show you any stinking badges!](https://www.youtube.com/watch?v=VqomZQMZQCQ)

<h3 align="center">
Status<br>
<a href="https://github.com/matteosox/nba/actions/workflows/data_pipeline.yaml"><img alt="Data Pipeline" src="https://github.com/matteosox/nba/actions/workflows/data_pipeline.yaml/badge.svg"></a>
<a href="https://github.com/matteosox/nba/actions/workflows/setup_test_push.yaml"><img alt="Setup, Test, & Build" src="https://github.com/matteosox/nba/actions/workflows/setup_test_push.yaml/badge.svg"></a>
<a href="https://nba.mattefay.com"><img alt="Website Status" src="https://img.shields.io/website?down_color=red&down_message=offline&label=nba.mattefay.com&up_color=brightgreen&up_message=online&url=https%3A%2F%2Fnba.mattefay.com"></a>
<br>Languages<br>
<a href="https://docs.python.org/3.8/"><img alt="Python: 3.8" src="https://img.shields.io/static/v1?label=Python&message=3%2C8&logo=python&color=%233776AB"></a>
<a href="https://www.gnu.org/software/bash/"><img alt="Bash: 5.1" src="https://img.shields.io/static/v1?label=Bash&message=5%2C1&logo=GNU-bash&color=%234EAA25"></a>
<a href="https://www.typescriptlang.org/"><img alt="Typescript: " src="https://img.shields.io/github/package-json/dependency-version/matteosox/nba/dev/typescript?filename=app%2Fpackage.json&logo=typescript&color=%233178C6&label=Typescript"></a>
<br>Services<br>
<a href="https://github.com/matteosox/nba"><img alt="VCS: Github" src="https://img.shields.io/static/v1?label=VCS&message=Github&logo=github&color=%23181717"></a>
<a href="https://github.com/matteosox/nba/actions"><img alt="CI: Github Actions" src="https://img.shields.io/static/v1?label=CI&message=Github%20Actions&logo=Github-Actions&color=%232088FF"></a>
<a href="https://hub.docker.com/repository/docker/matteosox/nba"><img alt="Container Repo: Docker Hub" src="https://img.shields.io/static/v1?label=Container%20Repo&message=Docker%20Hub&logo=Docker&color=%232496ED"></a>
<a href="https://protonvpn.com/"><img alt="VPN: ProtonVPN" src="https://img.shields.io/static/v1?label=VPN&message=ProtonVPN&logo=ProtonVPN&color=%2356B366"></a>
<a href="https://aws.amazon.com/s3/"><img alt="Storage: AWS S3" src="https://img.shields.io/static/v1?label=Storage&message=AWS%20S3&logo=Amazon-S3&color=%23569A31"></a>
<a href="https://vercel.com/matteosox/nba"><img alt="CD & Hosting: Vercel" src="https://img.shields.io/static/v1?label=CD%20%26%20Hosting&message=Vercel&logo=Vercel&color=%23000000"></a>
<a href="https://www.hover.com/"><img alt="Domain: Hover" src="https://img.shields.io/static/v1?label=Domain&message=Hover"></a>
<br>Dependencies<br>
<a href="https://jupyter.org/try"><img alt="Analysis environment: Jupyter" src="https://img.shields.io/static/v1?label=Analysis%20environment&message=Jupyter&logo=Jupyter&color=%23F37626"></a>
<a href="https://www.dynaconf.com/"><img alt="Config: Dynaconf" src="https://img.shields.io/static/v1?label=Config&message=Dynaconf"></a>
<a href="https://nextjs.org/"><img alt="Web framework: Next.js" src="https://img.shields.io/static/v1?label=Web%20framework&message=Next%2Cjs&logo=Next.js&color=%23000000"></a>
<a href="https://reactjs.org/"><img alt="UI: React" src="https://img.shields.io/static/v1?label=UI&message=React&logo=React&color=%2361DAFB"></a>
<a href="https://pbpstats.readthedocs.io/en/latest/"><img alt="NBA stats: pbpstats" src="https://img.shields.io/static/v1?label=NBA%20stats&message=pbpstats"></a>
<a href="https://docs.pymc.io/"><img alt="Models: pymc3" src="https://img.shields.io/static/v1?label=Models&message=pymc3"></a>
<br>Testing<br>
<a href="https://github.com/psf/black"><img alt="Python style: Black" src="https://img.shields.io/static/v1?label=Python%20style&message=Black&color=%23000000"></a>
<a href="https://www.pylint.org/"><img alt="Python quality: Pylint" src="https://img.shields.io/static/v1?label=Python%20quality&message=Pylint"></a>
<a href="https://www.shellcheck.net/"><img alt="Bash quality: ShellCheck" src="https://img.shields.io/static/v1?label=Bash%20quality&message=ShellCheck"></a>
</p>

## Info

### NBA Stats and Analysis

- Author: Matt Fay
- Email: matt.e.fay@gmail.com
- [Repo](https://github.com/matteosox/nba)
- [Site](https://nba.mattefay.com)

### Description

This repo has three main parts:
1) `pynba`: a Python package of stuff — utilities, data loaders/serializers, scripts — to analyze nba data.
2) `notebooks`: a collection of Jupyter notebooks analyzing nba data using `pynba`.
3) `app`: a Next.js web app hosted at [nba.mattefay.com](https://nba.mattefay.com), displaying the latest stats.

## User Notes

### Jupyter Notebook Environment

_TL;DR: To start up the notebook environment, run `notebooks/run.sh`, which will open up a browser tab for you._

We use a Dockerized Jupyter notebook environment for data analysis. The `notebooks/run.sh` bash script starts this container and opens up a web browser to the Jupyter server for you, with the repo mounted to `/home/jupyter/nba`. This allows you to edit the `pynba` package without needing to restart the container, since it is installed in [editable mode](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs). The Jupyter notebook directory is the repo's `notebooks` directory, which contains version controller notebooks. As well, the repo's `data` directory, ignored by Git, is mounted as well.

## TODO

- Analysis
    - Travel and rest adjustments
    - Re-evaluate priors
    - Confirm reduction in home court advantage
    - Fix 2020 bubble games
    - Playoffs?!
- App
    - Theme/style
    - Replace images with interactives
    - Improve tables (sortable, hover for definition, colorize for z-scores)

## Developer Notes

### Getting started

_TL;DR: Run `./developer_setup.sh`._

We use Docker for a clean environment within which to build, test, analyze, and so on. The `setup.sh` script in the `cicd` directory will build the relevant images for you. Running things natively isn't a supported/maintained thing.

In addition to docker, you'll need some developer secrets, in `build/notebook.local.env` and `build/app.local.env`. Those files are git ignored for obvious reasons, so you'll need to ask around to get those credentials.

To get you setup, you can run `./developer_setup.sh`. This will:
1) Symlink `test/pre-commit` to your `.git` directory, so that you'll automatically build and test code before you commit it.
2) Git only tracks a single executable bit for all files, so when setting up the repo, we need to set file permissions manually for files we need to write to from Docker. The `set_file_permissions.sh` script does this for you.

With all that out of the way, it then puts your machine through its paces by setting up, testing, and running various other workflows locally.

Finally, while you don't need it to do most workflows, it's probably a good idea to setup docker so you have push access to the Docker hub registry. That'll require a personal access token, which you can then use in combination with your Docker ID to login using `docker login`.

### Code Style

We use PEP8 for Python, but don't trip, just run `test/black_lint.sh` to get all your spaces in a row.

### Committing Code

We use the `pre-commit` git hook to run the settin' up and testin' phases of our CI/CD pipeline locally.

### Pull Requests

The `main` branch has [branch protections](https://help.github.com/en/github/administering-a-repository/about-protected-branches) turned on in Github, requiring one reviewer to approve a PR before merging. We also use the code owners feature to specify who can approve certain PRs. As well, merging a PR requires status checks to complete successfully.

When naming a branch, please use the syntax `firstname/branch-name-here`. If you plan to collaborate with others on that branch, use `team/branch-name-here`.

### Updating python requirements

_TL;DR: Run `requirements/update_requirements_in_docker.sh`._

There are two requirements files checked into this directory:
1) `requirements.in`
2) `requirements.txt`

The `.in` files are where we collect immediate dependencies, described in PyPI format (with versions pinned only as needed). The `.txt` files are generated by running the `requirements/update_requirements_in_docker.sh` script. This script runs the `requirements/update_requirements.sh` inside the `notebook` Docker container. We do this because `pip-compile` should be run from the same virtual environment as your project so conditional dependencies that require a specific Python version, or other environment markers, resolve relative to your project’s environment.

This gives us both a flexible way to describe dependencies while still achieving reproducible builds. Inspired by [this](https://hynek.me/articles/python-app-deps-2018/) and [this](https://pythonspeed.com/articles/pipenv-docker/).

### Handling Config

While the `constants.py` module contains values that don't change with each run, the `config.py` module makes configuration values available in the Python runtime that DO change. This uses [dynaconf](https://www.dynaconf.com/) to inject and load dynamic configuration from 1) `settings.toml` for defaults for each envionment, and 2) environment variables, prefixed with `PYNBA` and registered in `settings.toml`. The `meta_config.py` module provides a convenient syntax for creating a config dataclass with typed values that loads each parameter dynamically from `dynaconf`. You can see an example of this in the `config.py` module. The `dynaconf` environment is determined by the `ENV_FOR_DYNACONF` environment variable.

To pass environment variables into the Docker runtime, either for `dynaconf` or other purposes, you have two options:
1) export them in your development environment, then register them in the `notebook.env`. For example, to select a `dynaconf` environment other than `default`, you'll need to export it as `ENV_FOR_DYNACONF`. Note that this variable is already registered in `notebook.env` to be passed in.
2) add them to your `notebook.local.env` file, which is in the `.gitignore` so it won't be committed. This is where we keep developer credentials for example.

Inspired by the [12-factor application guide](https://12factor.net/config).

### Developing the NextJS App

_TL;DR: Run `app/run.sh`._

To ease developing the NextJS web app, we use `npm --prefix app run dev` in a Docker container with the app mounted. This starts the app in [development mode](https://nextjs.org/docs/api-reference/cli#development), which takes advantage of NextJS's [fast refresh](https://nextjs.org/docs/basic-features/fast-refresh) functionality, which catches exceptions and loads code updates near-instantaneously.

### Updating node packages

_TL;DR: Run `app/run.sh npm --prefix app update`._

To install a new npm package using `npm --prefix app install new-package`, you can use the same script with an optional command, e.g. `app/run.sh YOUR CMD HERE`. To update all packages, run `app/run.sh npm --prefix app update`.

## Continuous Integration

We use Github actions to run our CI pipeline on every pull request. The configuration can be found in `.github/workflows/setup_test_push.yaml`. That said, every step of CI can also be run locally.

### Settin' up

_TL;DR: To run tests, run `cicd/setup.sh`._

This builds the two relevant docker images, `notebook`, and `app`.

We do a couple of neat cacheing tricks to speed things up. First off, in the `Dockerfile`s themselves, we use the `RUN --mount=type=cache` functionality of Docker BuildKit to cache Python packages stored in `~/.cache/pip`. This keeps you local machine from re-downloading new Python packages each time. We don't use this for OS-level packages, i.e. those installed using `apt`, to reduce the size of the images. I tried and failed to get this to work for `npm install` and the `node_modules` directory, with mysteriously useless results. This was inspired by [this blog post](https://pythonspeed.com/articles/docker-cache-pip-downloads/)

Second, we use the new `BUILDKIT_INLINE_CACHE` feature to cache our images using Docker Hub. This is configured in the `docker build` command, and is smart enough to only download the layers you need. This was inspired by [this blog post](https://pythonspeed.com/articles/speeding-up-docker-ci/). This DOES work in Github Actions, while the prior functionality does not.

### Testin'

_TL;DR: To run tests, run `cicd/test.sh`._

#### Python Autoformatting

We use [`Black`](https://black.readthedocs.io/en/stable/index.html) to check our Python code for proper formatting. If it doesn't pass, you can autoformat your code using Black by running `test/black_lint.sh`. The settings for this can be found in `pyproject.toml`.

#### Python Linting

We use [`Pylint`](https://www.pylint.org/) for more general linting of our Python code. `Pylint` has some crazy settings and defaults, so use the `pylintrc` config file generously to use `pylint` to your favor, and not to your detriment.

#### Python Unit Tests

We use the built-in Python module `unittest`'s [test discovery](https://docs.python.org/3/library/unittest.html#test-discovery) functionality. This requires that all of the test files must be modules or packages importable from the root of the repo. As well, they must match the pattern `test*.py`. Our practice is to put tests for a module in a test folder in the same directory, which can then also contain data and other files needed to run those tests.

The package is installed using `setuptools`'s [`find_packages` function](https://setuptools.readthedocs.io/en/latest/setuptools.html#using-find-packages). We use the `exclude` feature to exclude all test code, i.e. `exclude=["*.tests", "*.tests.*", "tests.*", "tests"]`.

Thus, to run tests, we mount the root of the repo to the location in the container it's been installed. All of this is handled nicely by running `test.sh`, which uses the `notebook` container.

#### Bash Script Tests

We use [ShellCheck](https://github.com/koalaman/shellcheck) to test all the bash scripts in the repo. This helps us avoid some of the many sharp corners of bash, improving quality, readability, and style. This is run in `test/shellcheck.sh`.

#### Web App Tests

**TBD**

### Pushin'

_TL;DR: To push docker images to Docker Hub, run `cicd/push.sh`._

Note that you'll need to be logged in to Docker be able to do this locally. We use the `docker/login-action@v1` build action to login for the automated CI, and it uses a personal access token named `github-actions` from my Docker Hub account to do that, with the username and token stored as secrets.

In Docker Hub, we have one repository per image:
    - `notebook` -> `matteosox/nba-notebook`
    - `app` -> `matteosox/nba-app`

In addition to pushing each image with a tag as the git SHA of the code producing it, we also push an untagged (i.e. tagged as `latest`) image when pushing from the `main` branch.

### Buildin'

We don't build the Next.js app in the `setup_test_push.yaml` Github Actions workflow because Vercel is configured to do this for us. That said, as with all other CI workflows, we support running these locally. To build the app, use `app/build.sh`.

## Data Pipeline

We run a nightly data pipeline job using Github Actions to update the data hosted on the site. This is configured in `.github/workflows/data_pipeline.yaml`. Again, each step of the process can be run locally.

### VPN

Unfortunately, the NBA blocks API traffic from many cloud hosting providers, e.g. AWS. In our case, [Github Actions runs on Azure](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#cloud-hosts-for-github-hosted-runners). To get around this issue, I've setup a free ProtonVPN account. The various secrets needed to get that to work (a base certificate, TLS authentication key, and openvpn username & password) are stored as secrets in Github and injected as environment variables in the relevant step. An openvpn config file — `config.ovpn` — can be found in the `vpn` directory, along with a `connect.sh` bash script used by the workflow to set things up.

### Update Data

The first step of the data pipeline runs the `pynba_update` Python console script inside of the notebook Docker image using the `cicd/etl.sh` bash script. This queries for data for each league in the current year, saving any updates to the local data directory (mounted to the container). For seasons with new games found, we also calculate updated team ratings and generate updated plots.

### Sync Data to S3

The second (and final) step of the data pipeline runs the `pynba_sync` Python console script using the same environment/mechanism as before. This local data — pbpstats files, season parquet files, incremental possessions parquet files, team ratings & plots — is then synced to s3, where it can be accessed by the site.

### Github Actions Artifacts

We store an artifact of the local data directory at the completion of each run of the data pipeline, both for historical data, and ease of debugging.

## Continuous Deployment

The Python package `pynba` is strictly for code refactoring in this repo's Jupyter notebook environment, so it isn't packaged up and released, e.g. to PyPI.org.

### Vercel

The NextJS app is deployed to nba.mattefay.com by [Vercel](https://vercel.com/), the company behind NextJS. The deployment process is integrated with Github, so that any commit to the `main` branch results in a new deploy. Conveniently, Vercel also builds and deploys a "staging" site for every commit that changes the `app` directory, making them available through comments in your pull request for example.

Data and plots are stored in the `nba-mattefay` bucket on AWS S3. To access these files, we inject AWS credentials with environment variables. Unfortunately, Vercel [reserves the usual environment variables](https://vercel.com/docs/platform/limits#reserved-variables) for this, i.e. `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. To get around this, we store them as the non-standard `AccessKeyId` and `SecretAccessKey` environment variables, and manually load credentials in the `aws_s3.ts` javascript library, similar to [this approach](https://vercel.com/support/articles/how-can-i-use-aws-sdk-environment-variables-on-vercel) on Vercel's website. These credentials are from the `matteosox-nba-vercel` AWS IAM user, with read-only access to this one bucket.

To build the app locally (using `app/build.sh`), you should place your local AWS IAM credentials in `build/app.local.env`.

### DNS

I own the domain mattefay.com through hover.com. I host my blog there, using format.com. This repo's site is hosted at the nba.mattefay.com subdomain. Since [Vercel](https://vercel.com/) is hosting this site, I have a CNAME DNS record in Hover to alias that subdomain to them, i.e. `CNAME nba cname.vercel-dns.com`.
