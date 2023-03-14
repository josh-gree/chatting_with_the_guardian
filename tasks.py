import os
import shutil
from invoke import task


@task
def clean(ctx):
    for root, dirs, files in os.walk("."):
        # Remove __pycache__ directories
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))
            print(f"Removed: {os.path.join(root, '__pycache__')}")

        # Remove .pytest_cache directories
        if ".pytest_cache" in dirs:
            shutil.rmtree(os.path.join(root, ".pytest_cache"))
            print(f"Removed: {os.path.join(root, '.pytest_cache')}")

        # Remove .pyc files
        for file in files:
            if file.endswith(".pyc"):
                pyc_path = os.path.join(root, file)
                os.remove(pyc_path)
                print(f"Removed: {pyc_path}")


@task
def local_pg_up(ctx):
    ctx.run(
        "docker run --name pg -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:latest"
    )


@task
def local_pg_down(ctx):
    ctx.run("docker stop pg && docker rm pg")


@task
def local_run_migrations(ctx):
    run_migrations(ctx, True, "postgresql://postgres:password@localhost:5432/postgres")


@task
def sleep(ctx):
    ctx.run("sleep 1")


@task(local_pg_down, local_pg_up, sleep, local_run_migrations)
def local_reset(ctx):
    pass


@task
def install_dependencies(ctx):
    ctx.run("poetry install --with dev")


@task
def lint(ctx):
    ctx.run("ruff check .")


@task
def test(ctx):
    ctx.run("pytest")


@task
def run_migrations(ctx, prod, database_url):
    ctx.run(f"PROD={prod} DATABASE_URL={database_url} alembic upgrade head")
