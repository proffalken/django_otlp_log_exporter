import setuptools

with open("README.md", "r") as f:
    description = f.read()

setuptools.setup(
    name="django-otlp-log-exporter",
    version="1.1.0",
    author="Matthew Macdonald-Wallace",
    author_email="matt@doics.co",
    packages=["otlp_exporter"],
    description="integrate Django & SDK provided by OpenTelemetry and directly forward the logs from the application to OpenTelemetry.",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/proffalken/django_otlp_log_exporter",
    license='MIT',
    python_requires='>=3.7',
    install_requires=[
        'opentelemetry-sdk >= 1.16.0',
        'opentelemetry-api >= 1.16.0',
        'opentelemetry-exporter-otlp >= 1.16.0',
        'Django >= 3.2',
    ],
)
