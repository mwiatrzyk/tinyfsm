from invoke.tasks import task
from invoke.context import Context


@task(help={
    "format": "Coverage report format. [default: term]"
})
def report_coverage(ctx: Context, format: str="term"):
    """Create coverage report."""
    ctx.run(f"pytest --cov=tinyfsm --cov-branch --cov-report={format}")


@task(help={
    "port": "The port number to use. [default: 8080]"
})
def serve_coverage(ctx: Context, port: int=8080):
    """Create coverage report in HTML format and serve it locally."""
    ctx.run("inv report-coverage --format=html:reports/html")
    ctx.run(f"python -m http.server --directory reports/html {port}")
