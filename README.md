# KI/Tech-Briefing

Automatisches taegliches KI/Tech-Briefing als kostenlose GitHub-Pages-Seite.
Ein GitHub-Actions-Job laeuft jeden Morgen (~6 Uhr MESZ), holt die aktuellen
Top-Meldungen von der oeffentlichen Hacker-News-API und aktualisiert die Seite.
Kein eigener Server, kein API-Key, keine Kosten.

## Einrichtung (einmalig)

1. **Neues Repository anlegen**: Auf github.com ein neues, **oeffentliches** Repository erstellen (z.B. `ki-tech-briefing`).
2. **Dateien hochladen**: Den Inhalt dieses Ordners (inkl. `.github/`-Ordner!) in das Repo hochladen. Am einfachsten ueber "Add file" -> "Upload files" im Browser (ganzen Ordner reinziehen) oder per `git push`.
3. **Workflow-Rechte aktivieren**: Repo -> Settings -> Actions -> General -> "Workflow permissions" -> **"Read and write permissions"** auswaehlen -> Save. (Noetig, damit der Job die Seite committen darf.)
4. **GitHub Pages aktivieren**: Repo -> Settings -> Pages -> unter "Build and deployment" -> Source: **"Deploy from a branch"** -> Branch: **main**, Ordner: **/docs** -> Save.
5. **Ersten Lauf anstossen**: Repo -> Tab "Actions" -> Workflow "Daily AI/Tech Briefing" auswaehlen -> "Run workflow" klicken. Dauert ca. 1-2 Minuten.
6. **Link holen**: Nach dem Lauf ist die Seite live unter `https://<dein-github-username>.github.io/<repo-name>/`. Die URL steht auch unter Settings -> Pages.

## Aufs Handy bringen

1. Den Link (`https://<dein-username>.github.io/<repo-name>/`) auf dem Android-Handy in Chrome oeffnen.
2. Chrome-Menue (drei Punkte) -> "Zum Startbildschirm hinzufuegen".
3. Fertig — ab jetzt aktualisiert sich der Inhalt jeden Morgen automatisch im Hintergrund; beim Oeffnen der App siehst du den neuesten Stand.

## Anpassen

- Zeitplan aendern: `cron: "0 4 * * *"` in `.github/workflows/daily-briefing.yml` (Uhrzeit in UTC).
- Stichwoerter/Themen aendern: `KEYWORDS`-Regex in `scripts/build.py`.
- Anzahl Meldungen: `MAX_RESULTS` in `scripts/build.py`.
