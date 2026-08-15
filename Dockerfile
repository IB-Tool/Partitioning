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
    python3-pytest-cov \
    python3-coverage \
    python3-pip \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --no-cache-dir --break-system-packages pytest-timeout

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
# Ungepuffertes stdout/stderr, damit die CI-Logs live mitlaufen statt in
# einem Block-Puffer zu verschwinden, falls ein Test hängt.
ENV PYTHONUNBUFFERED=1

# Arbeitsverzeichnis für die Testausführung
WORKDIR /plugins/ibtoolpartion

# 6b. Übersetzungen kompilieren (i18n/*.ts -> *.qm) als Fallback für Aufrufe
#     ohne Volume-Mount (z.B. "docker run -it ... /bin/bash"). Für den
#     eigentlichen CI-Testlauf wirkungslos: dessen
#     "-v $(pwd):/plugins/ibtoolpartion" ersetzt den kompletten
#     /plugins/ibtoolpartion-Baum aus dem Image durch den Host-Checkout,
#     bevor CMD läuft - deshalb kompiliert CMD unten noch einmal und
#     maßgeblich. lrelease kommt mit qttools5-dev-tools, das im Basis-Image
#     bereits enthalten ist.
RUN for ts in i18n/*.ts; do lrelease "$ts"; done

# 7. Testsuite beim Containerstart ausführen.
#    xvfb-run stellt einen virtuellen X-Server bereit, falls QGIS trotz
#    QT_QPA_PLATFORM=offscreen intern einen Display benötigt.
#    --timeout bricht einen einzelnen hängenden Test nach 5 Minuten ab und
#    meldet ihn (statt dass der ganze CI-Job unbegrenzt hängen bleibt).
#    Die echo-Marker sind ein Diagnose-Hilfsmittel: Bisher gab es in den
#    CI-Logs an dieser Stelle NULL Ausgabe, selbst nach PYTHONUNBUFFERED=1.
#    Damit lässt sich beim nächsten Lauf sehen, ob schon xvfb-run/Xvfb
#    hängt oder erst pytest (Collection oder ein einzelner Test).
#    lrelease läuft hier erneut, weil *.qm Build-Artefakte sind und laut
#    .gitignore nicht eingecheckt werden - der Host-Checkout bringt sie
#    also nicht mit. Ohne diesen Schritt schlüge test_translations.py trotz
#    6b bei jedem CI-Lauf fehl.
CMD ["sh", "-c", "echo '[ci] compiling translations'; for ts in i18n/*.ts; do lrelease \"$ts\"; done; echo '[ci] launching xvfb-run'; xvfb-run -a sh -c 'echo \"[ci] Xvfb ready - starting pytest\"; python3 -m pytest --tb=short --timeout=300 --cov --cov-report=xml --cov-report=html'"]

