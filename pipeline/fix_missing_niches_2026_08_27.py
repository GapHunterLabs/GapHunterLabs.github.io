#!/usr/bin/env python3
"""
Script de correccion, corrido UNA VEZ el 2026-08-27 -- conservado como
registro historico, no forma parte del pipeline recurrente
(auto_update_catalog.py sigue siendo el unico que corre en cron).

CAUSA RAIZ: 67 de 101 plugins tenian el campo `niche` en
catalog_static_metadata.json como placeholder vacio ("—", un em dash
literal nunca reemplazado al agregar esos plugins -- mayormente la
"tanda fabrica" del 2026-08-19+), causando que TODOS cayeran en la
categoria catch-all "Other" del Hunting Field
(NICHE_TO_CATEGORY[p.niche] || 'other' en index.html). Encontrado al
investigar el reporte del usuario "el nodo Other se mantiene expandido
siempre" -- no era un bug de CSS/animacion/estado .active persistente,
el nodo era genuinamente ~2x mas grande que cualquier otro porque tenia
67 de 101 plugins reales (confirmado extrayendo los radios reales del
DOM renderizado: dot-ring r=50.6 para "other" vs. 25-31 para el resto,
retro-calculando el count real via la formula del radio).

QUE HIZO: asigno un niche real a cada uno de los 67, inferido de su
nombre/pitch, mismo criterio de especificidad que las ~34+23 entradas
del NICHE_TO_CATEGORY del sitio (nombres descriptivos, nunca
genericos) -- escribio directo sobre catalog_static_metadata.json.

DESPUES de correr esto, el swap del bloque <script id="catalog-data">
de index.html se hizo con un segundo paso INLINE (no versionado como
script aparte porque fue un one-off): leyo el catalog-data embebido
actual, hizo match por el campo `repo` contra catalog_static_metadata.json,
y actualizo SOLO el campo `niche` de cada plugin -- sin tocar
downloads/stars/growth/etc. que ya estaban frescos de la corrida diaria
real de auto_update_catalog.py. Las 23 entradas NUEVAS de niche que
salieron de esta asignacion se agregaron a mano al diccionario
NICHE_TO_CATEGORY dentro de index.html mismo (buscar el comentario
"23 niches added 2026-08-27" ahi).

Si un futuro plugin nuevo vuelve a entrar con niche="—" (placeholder sin
completar), el sintoma va a ser el mismo: "Other" crece de forma
desproporcionada en el Hunting Field. El chequeo rapido para confirmarlo
es el mismo usado aca: contar cuantos plugins de catalog_static_metadata.json
tienen `len(niche) <= 2`.
"""
import json

PATH = "catalog_static_metadata.json"

ASSIGNMENTS = {
    'apache-httpclient-reuse-companion': 'HTTP Client Reuse',
    'aws-sdk-client-reuse-companion': 'Cloud SDK Client Reuse',
    'cassandra-cqlsession-reuse-companion': 'Database Client Reuse',
    'elasticsearch-client-reuse-companion': 'Search Client Reuse',
    'gcp-client-reuse-companion': 'Cloud SDK Client Reuse',
    'kafka-producer-reuse-companion': 'Messaging Client Reuse',
    'ktor-httpclient-reuse-companion': 'HTTP Client Reuse',
    'micronaut-httpclient-create-companion': 'HTTP Client Reuse',
    'mongo-client-reuse-companion': 'Database Client Reuse',
    'object-mapper-reuse-companion': 'Object Mapper Reuse',
    'okhttp-client-reuse-companion': 'HTTP Client Reuse',
    'rabbitmq-channel-reuse-companion': 'Messaging Client Reuse',
    'redisson-client-reuse-companion': 'Cache Client Reuse',
    'connection-pool-config-companion': 'Connection Pool Tuning',
    'api-deprecation-header-companion': 'API Deprecation Tooling',
    'async-self-invocation-companion': 'Spring Framework Pitfalls',
    'binding-result-position-companion': 'Spring Framework Pitfalls',
    'correlation-id-propagation-companion': 'Distributed Tracing',
    'cors-policy-companion': 'API Security',
    'feign-fallback-config-companion': 'Resilience Tooling',
    'idempotency-key-companion': 'API Reliability',
    'rate-limiter-fallback-companion': 'Resilience Tooling',
    'resilience-self-invocation-companion': 'Spring Framework Pitfalls',
    'webhook-signature-companion': 'API Security',
    'config-secrets-file-companion': 'Secrets Detection',
    'jwt-signature-verification-companion': 'JWT / Auth Tooling',
    'php-file-inclusion-companion': 'PHP Security',
    'php-function-injection-companion': 'PHP Security',
    'php-open-redirect-companion': 'PHP Security',
    'php-shell-injection-companion': 'PHP Security',
    'php-sql-injection-companion': 'PHP Security',
    'ruby-shell-injection-companion': 'Ruby Security',
    'sql-concatenation-companion': 'SQL Injection Detection',
    'pii-field-annotation-companion': 'PII / Compliance',
    'dockerfile-layer-size-companion': 'Docker / DevOps',
    'dockerfile-unused-stage-companion': 'Docker / DevOps',
    'k8s-resource-limit-companion': 'Kubernetes Tooling',
    'gradle-task-graph-companion': 'Build Tooling / Architecture',
    'circular-dependency-companion': 'Build Tooling / Architecture',
    'changelog-fragment-companion': 'VCS / Git Workflow',
    'commit-message-convention-companion': 'VCS / Git Workflow',
    'merge-conflict-leftover-companion': 'VCS / Git Workflow',
    'semver-bump-mismatch-companion': 'VCS / Git Workflow',
    'log-format-string-companion': 'Code Quality / Logging',
    'micrometer-timer-sample-companion': 'Observability Tooling',
    'otel-span-naming-companion': 'Distributed Tracing',
    'prometheus-metric-naming-companion': 'Observability Tooling',
    'prometheus-metric-registration-companion': 'Observability Tooling',
    'http-status-inline-companion': 'Editor Productivity',
    'json-path-builder-companion': 'JSON Schema Tooling',
    'kafka-topic-schema-companion': 'Data Format Conversion',
    'postman-openapi-drift-companion': 'OpenAPI/Swagger Tooling',
    'grpc-error-status-companion': 'gRPC Tooling',
    'grpc-streamobserver-contract-companion': 'gRPC Tooling',
    'env-var-missing-companion': 'Env Config Tooling',
    'feature-flag-reference-companion': 'Code Quality / Feature Flags',
    'flaky-test-marker-companion': 'Testing / Codegen',
    'n-plus-one-query-companion': 'Database Performance',
    'regex-named-group-companion': 'Regex Tooling',
    'rxjava-disposable-leak-companion': 'Code Quality / Logging',
    'go-timer-leak-companion': 'Code Quality / Logging',
    'npm-peer-dependency-companion': 'Node.js / npm Tooling',
    'php-composer-script-companion': 'Node.js / npm Tooling',
    'unused-npm-script-companion': 'Node.js / npm Tooling',
    'ruby-gemfile-group-companion': 'VCS / Git Workflow',
    'ruby-nethttp-reuse-companion': 'HTTP Client Reuse',
    'rails-mass-assignment-companion': 'Ruby Security',
}


def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)
    plugins = data["plugins"]

    applied = 0
    for repo, niche in ASSIGNMENTS.items():
        if repo not in plugins:
            print("!! repo no encontrado en metadata:", repo)
            continue
        plugins[repo]["niche"] = niche
        applied += 1

    still_missing = [r for r, v in plugins.items() if len(v.get("niche", "")) <= 2]

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("aplicados:", applied)
    print("aun sin niche real:", len(still_missing), still_missing)


if __name__ == "__main__":
    main()
