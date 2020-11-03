# NVDA Unmute

* Autor: Oleksandr Gryshchenko
* Wersja: 1.4
* Pobierz [wersja stabilna][1]
* Pobierz [wersja rozwojowa][2]

Ten dodatek sprawdza stan systemu audio Windows podczas uruchamiania NVDA. Jjeśli okaże się, że dźwięk jest wyciszony - dodatek na siłę go włącza.
Dodatek sprawdza również stan syntezatora mowy. W przypadku problemów z jego inicjalizacją podejmowane są próby uruchomienia syntezatora, co jest określone w ustawieniach NVDA.

## Okno dialogowe ustawień dodatku
W oknie dialogowym ustawień dodatku dostępne są następujące opcje:

1. Pierwszy suwak w oknie dialogowym ustawień dodatków pozwala określić poziom głośności systemu Windows, który zostanie ustawiony po uruchomieniu NVDA, jeśli dźwięk był wcześniej wyciszony lub był za cichy.

2. Minimalny poziom głośności systemu Windows, przy którym zostanie zastosowana procedura zwiększania głośności. Ten suwak umożliwia dostosowanie poziomu czułości dodatku.
Jeśli poziom głośności spadnie poniżej wartości podanej w tym miejscu, głośność zostanie zwiększona przy następnym uruchomieniu NVDA.
W przeciwnym wypadku, jeśli poziom głośności pozostanie wyższy niż wartość określona w tym miejscu, to po ponownym uruchomieniu NVDA jego poziom się nie zmieni.
I oczywiście, jeśli dźwięk był wcześniej wyłączony, po ponownym uruchomieniu dodatek i tak go włączy.

3. Poniższe pole wyboru umożliwia włączenie ponownej inicjalizacji sterownika syntezatora mowy.
Ta procedura rozpocznie się tylko wtedy, gdy zostanie podczas uruchamiania NVDA wykryte, że sterownik syntezatora mowy nie został zainicjowany.

4. W tym polu możesz określić liczbę prób ponownej inicjalizacji sterownika syntezatora mowy. Próby są wykonywane cyklicznie w odstępie 1 sekundy. Wartość 0 oznacza, że ​​próby będą wykonywane w nieskończoność, aż do pomyślnego zakończenia procedury.

5. Następne pole wyboru włącza lub wyłącza odtwarzanie dźwięku startowego, gdy operacja zakończy się pomyślnie.

## Lista zmian

### Version 1.4
* dodano metodę zwiększania głośności startowej oddzielnie dla procesu NVDA;
* wszystkie funkcje ręcznej regulacji głośności zostały przeniesione do dodatku NVDA Volume Adjustment.

### Wersja 1.3
* dodano możliwość sterowania głośnością głównego urządzenia audio i osobno dla każdego uruchomionego programu;
* zaktualizowano tłumaczenie na język wietnamski (podziękowania dla Dang Manh Cuong);
* dodano tłumaczenie na język turecki (podziękowania dla Cagri Dogan);
* dodano tłumaczenie na język włoski (podziękowania dla Christianlm);
* dodano tłumaczenie na język chiński uproszczony (podziękowania dla Cary Rowen);
* dodano tłumaczenie na język polski (podziękowania dla Stefan Banita);
* zaktualizowano tłumaczenie na język ukraiński;
* zaktualizowano plik ReadMe.

### Wersja 1.2
* przełączono na używanie **Core Audio Windows API** zamiast **Windows Sound Manager**;
* dodano odtwarzanie dźwięku startowego, gdy dźwięk zostanie pomyślnie włączony przez dodatek.

### Wersja 1.1
* dodano okno dialogowe ustawień dodatku;
* zaktualizowano tłumaczenie na język ukraiński.

### Wersja 1.0.1
* Wykonuje wielokrotne próby włączenia sterownika syntezatora w przypadku niepowodzenia jego inicjalizacji;
* Dodano tłumaczenie na język wietnamski przez Dang Manh Cuong;
* Dodano tłumaczenie na język ukraiński.

### Wersja 1.0. Zaimplementowano funkcje
Dodatek korzysta z zewnętrznego modułu Windows Sound Manager.

## Zmiany w NVDA Unmute
Możesz sklonować to repozytorium, aby wprowadzić zmiany w NVDA Unmute.

### Zewnętrzne zależności
Można je zainstalować za pomocą pip:
- markdown
- scons
- python-gettext

### Aby spakować dodatek do dystrybucji:
1. Otwórz wiersz poleceń, przejdź do katalogu głównego tego repozytorium
2. Uruchom polecenie **scons**. Utworzony dodatek, jeśli nie było błędów, jest umieszczony w bieżącym katalogu.

[1]: https://github.com/grisov/Unmute/releases/download/v1.4/unmute-1.4.nvda-addon
[2]: https://github.com/grisov/Unmute/releases/download/v1.4/unmute-1.4.nvda-addon
