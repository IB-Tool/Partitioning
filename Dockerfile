FROM python:3.11-slim

# Install test dependencies at build time; source code is mounted at runtime.
COPY requirements-test.txt /tmp/requirements-test.txt
RUN pip install --no-cache-dir -r /tmp/requirements-test.txt

WORKDIR /plugins/ibtoolpartion

# Run the full test suite with coverage when the container starts.
# coverage.xml is written to WORKDIR, which maps to the host volume mount
# ($(pwd)) so the CI step can read it after the container exits.
CMD ["python", "-m", "pytest", \
     "--cov=.", \
     "--cov-report=xml:coverage.xml", \
     "--cov-report=term-missing", \
     "--tb=short"]
