# AGENTS.md - fastapi-users-admin

## Zweck

Dieses Paket stellt eine wiederverwendbare Benutzerverwaltung fuer FastAPI-Anwendungen bereit.
Es umfasst Admin-CRUD, Profil- und Passwortverwaltung, Superuser-Schutz, eine HTML-Admin-Oberflaeche
und austauschbare Service-Implementierungen.

## Sicherheitsregeln

- Alle Admin-Endpunkte muessen ueber die vorhandenen Auth-Dependencies und die Superuser-Pruefung
  geschuetzt bleiben.
- Selbst-Heraufstufung zum Superuser und andere Privilege-Escalation-Pfade verhindern.
- Passwoerter niemals speichern oder loggen; ausschliesslich `SecurityUtils` zum Hashen und
  Verifizieren verwenden.
- Passwort-Reset-Tokens, Session-Tokens, SMTP-Passwoerter und andere Secrets niemals in Logs,
  API-Antworten oder Templates ausgeben.
- Login-, Reset- und Benutzerabfragen so gestalten, dass keine User-Enumeration durch
  unnoetig unterschiedliche Antworten entsteht.
- Superuser duerfen sich nicht ueber den vorgesehenen Selbstloesch-Endpunkt loeschen.
- E-Mail- und SMTP-Konfiguration nur ueber sichere externe Konfiguration einlesen; keine Secrets
  in Beispielen oder Tests committen.

## Projektstruktur

- `models/admin_models.py`: Pydantic-Modelle fuer Create, Update, Public, Listen und Passwort-
  Operationen
- `services/base_user_admin_service.py`: Backend-unabhaengiger Service-Vertrag
- `services/user_admin_service.py`: SQLAlchemy-Implementierung fuer Benutzer-CRUD
- `services/user_crud_service.py`: Wiederverwendbare CRUD-Hilfsfunktionen
- `dependencies/admin_deps.py`: aktive Benutzer-, Superuser- und HTML-Redirect-Dependencies
- `routers/user_admin_router.py`: REST-Endpunkte und HTML-Admin-Seite
- `config/admin_config.py`: API-Prefix, Templates, E-Mail, Reset-Token und Logging
- `utils/security_utils.py` / `email_utils.py`: Sicherheits- und E-Mail-Hilfen
- `templates/`: ausgelieferte Admin-HTML-Templates
- `examples/`: Integrations- und Multi-Provider-Beispiele
- `test_module.py`: grundlegende Service- und Security-Tests

## Integrationsregeln

- `UserAdminRouter` mit einer echten Datenbank-Session-Dependency, dem passenden User-ORM-Modell,
  `AuthDependencies` und `SecurityUtils` initialisieren.
- Datenbank-Session und User-Modell injizieren; keine globale Engine oder Session im Paket
  einfuehren.
- Neue Backend-Implementierungen von `BaseUserAdminService` ableiten und denselben CRUD-Vertrag
  einhalten.
- Aenderungen an User-Modellfeldern, UUID-/ID-Behandlung oder Passwortspalten mit dem verwendeten
  Auth-Modul und den Datenbankmigrationen abstimmen.
- `AdminConfig.templates_dir` nur auf vertrauenswuerdige Template-Verzeichnisse zeigen lassen.
  Neue Templates muessen als Package-Daten ausgeliefert werden.
- Neue oeffentliche Symbole ueber `fastapi_users_admin.__init__` exportieren und bestehende
  Importpfade kompatibel halten.

## API- und Service-Verhalten

- Validierung ueber die vorhandenen Pydantic-Modelle nutzen; Mindestlaenge fuer neue Passwoerter nicht
  umgehen.
- E-Mail-Eindeutigkeit vor dem Anlegen oder Aendern eines Benutzers pruefen.
- Aenderungen am eigenen Profil duerfen keine administrativen Privilegien erhoehen.
- `UserAdminPublic` darf keine Passwort- oder Hash-Felder enthalten.
- SQLAlchemy-Operationen ueber den injizierten Service und die vorhandene Session durchfuehren;
  Commit, Refresh und Fehlerbehandlung konsistent halten.
- Bei fehlendem Benutzer oder fehlender Berechtigung explizite, passende HTTP-Fehler liefern.

## Vorgehen bei Aenderungen

1. Betroffene Schichten identifizieren: Models, Dependencies, Router, Service und Konfiguration.
2. Sicherheitsrelevante Aenderungen mit positiven und negativen Tests abdecken.
3. API-Routen, Statuscodes und Response-Modelle in den Integrationsbeispielen und der README
   nachfuehren.
4. Bei Datenmodellaenderungen die Migrationen und die Kompatibilitaet mit `fastapi-users-auth`
   pruefen.

## Qualitaetssicherung

Aus dem Paketverzeichnis:

```bash
pip install -e ".[dev]"
pytest -q
ruff check .
mypy .
```

Besonders pruefen: fehlende oder inaktive Benutzer, nicht privilegierte Zugriffe, Superuser-
Schutz, Passwortwechsel, Passwort-Reset, E-Mail-Duplikate, Public-Response-Felder und die
Template-Auslieferung.

## Nicht tun

- Keine Authentifizierungs- oder Superuser-Pruefungen durch direkte Datenbankabfragen umgehen.
- Keine breite Ausnahmebehandlung einfuehren, die Sicherheitsfehler oder fehlende Dependencies
  verschleiert.
- Keine Tokens, Passwoerter oder kompletten User-Objekte mit sensiblen Feldern loggen.
- Keine manuellen Aenderungen an `.idea`-, Cache- oder Build-Dateien.
