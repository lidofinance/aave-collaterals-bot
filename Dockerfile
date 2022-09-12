FROM python:3.10.7-slim-bullseye as base

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install --no-install-recommends -y curl=7.74.0-1.3+deb11u3 tini=0.19.0-1 && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.2.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    APP_PATH="/usr/app" \
    VENV_PATH="/usr/app/.venv"

ENV PATH="$VENV_PATH/bin:$PATH"


FROM base as deps

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

ENV PATH="$POETRY_HOME/bin:$PATH"
WORKDIR $APP_PATH

RUN apt-get update && apt-get install -y --no-install-recommends build-essential=12.9
RUN curl -sSL https://install.python-poetry.org | python -

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --only main


FROM base as prod

RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python

WORKDIR $APP_PATH
RUN chown -R python:python .

COPY --chown=python:python --from=deps $VENV_PATH $VENV_PATH
COPY --chown=python:python ./src .
COPY --chown=python:python build-info.json .

USER python
HEALTHCHECK --interval=10s --timeout=3s CMD sh -c "curl -f http://localhost:${EXPORTER_PORT:-8080}/healthcheck || exit 1"
ENTRYPOINT ["tini", "--", "python"]
CMD ["main.py"]
