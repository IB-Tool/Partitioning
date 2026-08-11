# 1. Basis-Image mit QGIS 3.40
FROM 3liz/qgis-platform:3.40

# 2. Root-Rechte für Systeminstallationen
USER root

# 3. System-Updates, Headless-X-Server und Test-Abhängigkeiten installieren.
#    Diese Plugin hat keine Runtime-Abhängigkeiten außerhalb der QGIS-eigenen
#    Prozessierungs-Algorithmen (siehe requirements-test.txt für Test-Deps).
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    xvfb \
    python3-pytest \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*

# 4. Arbeitsverzeichnis im Container
WORKDIR /plugins

# 5. Plugin-Code kopieren. Der Ordnername ist bereits ein gültiger
#    Python-Bezeichner, daher ist (anders als bei IB-Tool-3) kein
#    virtuelles Package-Alias nötig.
COPY . /plugins/ibtoolpartion/

# 6. Umgebungsvariablen für headless mode und Processing setzen
ENV QT_QPA_PLATFORM=offscreen
ENV QGIS_PREFIX_PATH=/usr
ENV PYTHONPATH=/plugins:/usr/share/qgis/python:/usr/share/qgis/python/plugins
ENV QGIS_PLUGINPATH=/usr/share/qgis/python/plugins

# Arbeitsverzeichnis für die Testausführung
WORKDIR /plugins/ibtoolpartion

# 7. Testsuite beim Containerstart ausführen.
#    xvfb-run stellt einen virtuellen X-Server bereit, falls QGIS trotz
#    QT_QPA_PLATFORM=offscreen intern einen Display benötigt.
CMD ["xvfb-run", "-a", "python3", "-m", "pytest", "--tb=short"]

