# NVDA Stummschaltung aufheben

* Autor: Oleksandr Gryshchenko
* Version: 1.6
* NVDA-Kompatibilität: 2025.1 und höher
* Download: [stabile Version][1]

Diese Erweiterung überprüft beim Start von NVDA den Status des Windows-Audiosystems. Wenn sich herausstellt, dass der Ton stummgeschaltet ist, erzwingt diese Erweiterung die Aufhebung der Stummschaltung. Gleichzeitig wird auch die Lautstärke für den NVDA-Prozess überprüft.

Die Erweiterung überprüft auch den Status des Sprachsynthesizers. Wenn Probleme bei der Initialisierung auftreten, wird versucht, den in den NVDA-Einstellungen angegebenen Synthesizer zu starten.

Es besteht zusätzlich die Möglichkeit zu überprüfen, über welches Audiogerät der NVDA-Ton ausgegeben wird. Wenn dieses Gerät vom Standardgerät abweicht, wird die Ausgabe automatisch auf das im System als Standardgerät installierte Audiogerät umgeschaltet.

Hinweis: Wenn der Startton der Erweiterung immer abgespielt wird, auch wenn die NVDA-Lautstärke bereits richtig eingestellt ist, bedeutet das, dass die Erweiterung die Ausgabe bei jedem Start von NVDA auf das Standardaudiogerät umschaltet.

Dies tritt auf, wenn das Audioausgabegerät in den NVDA-Einstellungen vom Standardausgabegerät oder „Microsoft Sound Mapper” abweicht.

Dies lässt sich auf eine der folgenden Arten leicht beheben:

1. Speichern Sie nach dem Neustart von NVDA einfach die aktuelle Konfiguration mit NVDA+Strg+C. Das Standard-Audiogerät wird in den NVDA-Einstellungen gespeichert und die Umschaltung erfolgt nicht mehr bei jedem Start von NVDA.
2. Wenn Sie die NVDA-Konfiguration nicht ändern möchten, deaktivieren Sie einfach die Funktion zum Umschalten der Audiogeräte im Einstellungsdialog „Stummschaltung aufheben”.

## Einstellungsdialog der Erweiterung

Um die Einstellungen der Erweiterung zu öffnen, gehen Sie wie folgt vor:

* Drücken Sie NVDA+N, um das NVDA-Menü zu öffnen.
* Gehen Sie dann zu „Optionen“ -> „Einstellungen...“ und suchen Sie in der Kategorienliste „Stummschaltung aufheben“.

Das war's schon, Sie können nun mit der Tabulatortaste zwischen den Einstellungen wechseln.

Im Einstellungsdialog der Erweiterung stehen die folgenden Optionen zur Verfügung:

1. Mit dem ersten Schieberegler können Sie die Lautstärke von Windows festlegen, die beim Start von NVDA eingestellt wird, wenn der Ton zuvor stummgeschaltet oder zu leise war.

2. Die minimale Windows-Lautstärke, bei der die Lautstärke erhöht wird. Mit diesem Schieberegler können Sie die Empfindlichkeit einstellen. Wenn die Lautstärke unter den hier angegebenen Wert fällt, wird die Lautstärke beim nächsten Start von NVDA erhöht. Andernfalls, wenn die Lautstärke über dem hier angegebenen Wert bleibt, ändert sich die Lautstärke beim Neustart von NVDA nicht. Und natürlich wird der Ton, wenn er zuvor ausgeschaltet war, beim Neustart von NVDA trotzdem eingeschaltet.

3. Mit dem folgenden Kontrollkästchen können Sie die Neuinitialisierung des Sprachsynthesizer-Treibers aktivieren. Dieser Vorgang wird nur gestartet, wenn beim Start von NVDA festgestellt wird, dass der Sprachsynthesizer-Treiber nicht initialisiert wurde.

4. In diesem Feld können Sie die Anzahl der Versuche zur Neuinitialisierung des Sprachsynthesizer-Treibers festlegen. Die Versuche werden zyklisch im Abstand von 1 Sekunde durchgeführt. Der Wert 0 bedeutet, dass die Versuche so lange wiederholt werden, bis der Vorgang erfolgreich abgeschlossen ist.

5. Mit der Option „Zum Standard-Audioausgabegerät wechseln“ können Sie beim Start überprüfen, über welches Audiogerät NVDA-Töne ausgegeben werden. Wenn dieses Gerät vom Standardgerät abweicht, wird die Ausgabe automatisch auf das im System als Standardgerät installierte Audiogerät umgeschaltet.

6. Das nächste Kontrollkästchen aktiviert oder deaktiviert die Wiedergabe des Starttons, wenn der Vorgang erfolgreich war.

## Komponenten von Drittanbietern

Die Erweiterung verwendet die folgenden Komponenten von Drittanbietern:

* Für die Interaktion mit der **Windows Core Audio API** – [PyCaw-Modul](https://github.com/AndreMiras/pycaw/), das unter der MIT-Lizenz vertrieben wird.
* Zum Abrufen von Informationen über laufende Prozesse und zur Verwendung der PyCaw-Komponente – [psutil-Modul](https://github.com/giampaolo/psutil), das unter der BSD-3-Lizenz vertrieben wird.

## Änderungsprotokoll

### Version 1.5.7
* Die Erweiterung wurde auf Kompatibilität mit NVDA 2023.1 getestet.

### Version 1.5.6
* Die Erweiterung wurde auf Kompatibilität mit NVDA 2022.1 getestet.
* Das Drittanbieter-Modul **psutil** wurde aktualisiert.
* Die Erweiterung wurde für die Python-Versionen 3.7 und 3.8 angepasst.
* MyPy-Typ-Annotationen zum Quellcode der Erweiterung hinzugefügt;
* Funktion „Zum Standard-Audioausgabegerät wechseln” hinzugefügt;
* Die Erweiterungs-Parameter werden immer im Basis-Konfigurationsprofil gespeichert;
* Spanische und galicische Übersetzungen hinzugefügt (danke an Ivan Novegil Cancelas und Jose Manuel);
* Übersetzung ins Vietnamesische aktualisiert (danke an Dang Manh Cuong).

### Version 1.4
* Methode zum separaten Erhöhen der Startlautstärke für den NVDA-Prozess hinzugefügt;
* Akustische Benachrichtigung bei erfolgreicher Ausführung geändert (danke an Manolo);
* Alle manuellen Lautstärkeregelungsfunktionen wurden in die Erweiterung „NVDA Volume Adjustment” übertragen.

### Version 1.3
* Möglichkeit hinzugefügt, die Lautstärke des Standardaudiogeräts und des laufenden Programms separat zu steuern;
* Übersetzung ins Vietnamesische aktualisiert (danke an Dang Manh Cuong);
* Türkische Übersetzung hinzugefügt (danke an Cagri Dogan);
* Italienische Übersetzung hinzugefügt (danke an Christianlm);
* Vereinfachte chinesische Übersetzung hinzugefügt (danke an Cary Rowen);
* Polnische Übersetzung hinzugefügt (danke an Stefan Banita);
* Ukrainische Übersetzung aktualisiert;
* ReadMe aktualisiert.

### Version 1.2
* Umstellung auf die Verwendung der **Core Audio Windows API** anstelle des **Windows Sound Managers**;
* Startton wird abgespielt, wenn die Audioausgabe durch die Erweiterung erfolgreich aktiviert wurde.

### Version 1.1
* Erweiterungs-Einstellungsdialog hinzugefügt;
* Ukrainische Übersetzung aktualisiert.

### Version 1.0.1
* Wiederholte Versuche, den Synth-Treiber zu aktivieren, falls die Initialisierung fehlschlägt;
* Vietnamesische Übersetzung von Dang Manh Cuong hinzugefügt;
* Ukrainische Übersetzung hinzugefügt.

### Version 1.0

Funktionen der Implementierung
Die Erweiterung verwendet ein Drittanbieter-Modul namens Windows Sound Manager.

## Ändern des Erweiterungs-Quellcodes
Sie können dieses Repository klonen, um Änderungen an NVDA Unmute vorzunehmen.

### Abhängigkeiten von Drittanbietern

Diese können mit pip installiert werden:

- markdown
- scons
- python-gettext

### So packen Sie die Erweiterung für die Verteilung

1. Öffnen Sie eine Befehlszeile und wechseln Sie zum Stammverzeichnis dieses Repositorys.
2. Führen Sie den Befehl **scons** aus. Das erstellte Erweiterung wird, sofern keine Fehler aufgetreten sind, im aktuellen Verzeichnis abgelegt.

[1]: https://addons.nvda-project.org/files/get.php?file=unmute
