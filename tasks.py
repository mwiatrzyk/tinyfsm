from invoke.tasks import task
from invoke.context import Context

LINE_LENGTH = 120


@task(help={"fix": "Fix code formatting."})
def check_format(ctx: Context, fix: bool = False):
    """Check if code is formatted."""
    ctx.run(f"ruff format --line-length={LINE_LENGTH} {'--check' if not fix else ''}")


@task(help={"fix": "Fix fixable linter errors."})
def check_lint(ctx: Context, fix: bool = False):
    """Check code against linting errors."""
    ctx.run(f"ruff check --exclude api.py {'--fix' if fix else ''}")


@task
def check_tests(ctx: Context):
    """Check if all tests are passing."""
    ctx.run("pytest")


@task
def check_coverage(ctx: Context):
    """Check code coverage."""
    ctx.run("pytest --cov=tinyfsm --cov-branch --cov-fail-under=100")


@task(check_format, check_lint, check_tests, check_coverage)
def check(ctx: Context):
    """Run all checks."""


@task(help={"format": "Coverage report format. [default: term]"})
def report_coverage(ctx: Context, format: str = "term"):
    """Create coverage report."""
    ctx.run(f"pytest --cov=tinyfsm --cov-branch --cov-report={format}")


@task(help={"port": "The port number to use. [default: 8080]"})
def serve_coverage(ctx: Context, port: int = 8080):
    """Create coverage report in HTML format and serve it locally."""
    ctx.run("inv report-coverage --format=html:reports/html")
    ctx.run(f"python -m http.server --directory reports/html {port}")


@task
def build(ctx: Context):
    """Build Python package."""
    ctx.run("poetry build")


@task
def build_deploy_key(ctx: Context, comment: str = "CircleCI"):
    """Build a deploy key to use in CI/CD pipeline."""
    ctx.run("rm -rf ssh")
    ctx.run("mkdir -p ssh")
    ctx.run(f"ssh-keygen -t ed25519 -C {comment} -f ssh/ed25519")


@task
def bump(ctx: Context, dry_run: bool = False):
    """Create next version."""
    ctx.run(f"bumpify {'--dry-run' if dry_run else ''} bump")


@task
def publish(ctx: Context):
    """Publish Python package to PyPI."""
    ctx.run("poetry publish")
