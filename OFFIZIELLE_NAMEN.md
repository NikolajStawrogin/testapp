# Recherche: amtliche Namen für Taipei City und New Taipei City

Stand: 3. November 2026. Recherche und Planung, kein Anwendungscode.

## Ergebnis und Belastbarkeit

Der stärkste gefundene Kandidat für traditionelle chinesische Straßennamen mit amtlicher englischer Schreibweise ist der Downloadbereich der taiwanischen Post, 中華郵政 (Chunghwa Post). Mehrere unabhängig veröffentlichte Projekte verweisen auf deren Straßen-, benannte-Gassen- und Bezirksverzeichnisse.

Die Downloadverweise führen auf eine amtliche Domain. Ihre gegenwärtigen Inhalte konnten in dieser Umgebung wegen eines HTTP-403-Fehlers des Proxys nicht direkt gelesen werden. Erfolgreich gelesen und inhaltlich geprüft wurden öffentlich bereitgestellte Kopien eines privaten GitHub-Projekts. Deshalb gilt:

- Konkrete amtliche Ursprungsquelle mit Dateinamen und Downloadverweisen identifiziert.
- Inhalte, Umfang und Prüfsummen der untersuchten Kopien überprüft.
- Authentizität gegenüber dem aktuellen Postserver, neueste verfügbare Ausgabe, ursprüngliche Weiterverwendungsbedingungen und Übereinstimmung mit allen heutigen Taipei-Straßenschildern noch nicht abschließend verifiziert.

Eine passende Referenzquelle ist damit gefunden; ein vollständiger aktueller amtlich verifizierter Taipei-Quizkatalog liegt noch nicht vor.

## 1. Kandidaten auf amtlichen Domains

### Chunghwa Post: Downloadbereich und Adressübersetzung

- [Downloadbereich, Abschnitt 6 laut den untersuchten Projekten](https://www.post.gov.tw/post/internet/Download/all_list.jsp?ID=2201)
- [Offizielles Werkzeug zur englischen Adressdarstellung](https://www.post.gov.tw/post/internet/Postal/index.jsp?ID=207)

| Verzeichnis | Inhalt der untersuchten Kopie | Zugeordnete Ausgabe laut Quellenmanifest |
| --- | --- | --- |
| 路街中英對照文字檔 / 中英文街路名稱對照檔 | Chinesisch-englische Straßennamen einschließlich zahlreicher Sections und benannter Gassen | 113/01, Dateidatum 1. April 2024 |
| 村里文字巷中英對照文字檔 | Namen von Dörfern, kleineren Verwaltungseinheiten und benannten Lanes | 113/01 |
| 縣市鄉鎮中英對照 Xml 檔 | Chinesische und englische Stadt-/Bezirksnamen mit dreistelligem Postcode | 109/06, XML-Erzeugungsdatum 12. Juni 2020 |

Das taiwanische Kalenderjahr 113 entspricht 2024, 109 entspricht 2020. Diese Ausgaben sind keine Aussage darüber, welche Version heute die neueste ist.

Konkrete Originalverweise aus dem untersuchten Quellenmanifest, noch nicht direkt abrufbar:

- [Straßenliste: 中英文街路名稱對照檔1130401.TXT](https://www.post.gov.tw/post/download/%E4%B8%AD%E8%8B%B1%E6%96%87%E8%A1%97%E8%B7%AF%E5%90%8D%E7%A8%B1%E5%B0%8D%E7%85%A7%E6%AA%941130401.TXT)
- [Benannte Gassen und kleinere Verwaltungseinheiten: 村里文字巷中英對照.TXT](https://www.post.gov.tw/post/download/%E6%9D%91%E9%87%8C%E6%96%87%E5%AD%97%E5%B7%B7%E4%B8%AD%E8%8B%B1%E5%B0%8D%E7%85%A7.TXT)
- [Städte und Bezirke: County_h_10906.xml](https://www.post.gov.tw/post/download/County_h_10906.xml)

Ein weiteres Projekt verweist unabhängig auf die ältere Excel-Ausgabe [6.5_CEROAD11107.xlsx](https://www.post.gov.tw/post/download/6.5_CEROAD11107.xlsx), bezeichnet als 路街中英對照Excel檔 111/07 (漢語拼音). Das bestätigt den Quellenpfad als Recherchehinweis, ersetzt aber keinen eigenen Abruf der Primärquelle.

### Weitere amtliche Rechercheziele

- [Open-Data-Portal Taipei](https://data.taipei/): benötigt für aktuelle Stadt-/Bezirkszuordnung, Straßenexistenz, mögliche lokale Namensverzeichnisse und Geometrien. Ein konkreter passender Datensatz konnte noch nicht direkt geprüft werden.
- [Taiwans staatliches Datenportal](https://data.gov.tw/): zusätzlicher Suchweg zu amtlichen Beständen und deren Lizenzmetadaten; ebenfalls direkt blockiert.
- [Englisches Portal der Stadt Taipei](https://english.gov.taipei/): möglicher Abgleich mit städtischen Schreibweisen. Noch kein Ersatz für einen vollständigen Straßendatensatz.

## 2. Tatsächlich untersuchte Dateien

Die Dateien stammen aus dem privaten Projekt `sean1093/menpai`, nicht aus einem amtlichen GitHub-Konto. Das Projekt beschreibt sie als aus Big5 nach UTF-8 umkodierte Kopien der Postverzeichnisse. Diese Herkunftsangabe bleibt eine Angabe des Projekts, solange kein direkter Vergleich mit den Originalen möglich ist.

Untersuchte feste Git-Version: `2a5923e5de751e24586901082a7df80653e7a96e`.

- [Quellenmanifest mit Original-URLs, Ausgaben und Prüfsummen](https://github.com/sean1093/menpai/blob/2a5923e5de751e24586901082a7df80653e7a96e/data/source/SOURCE.md)
- [Straßenkopie: roads.csv](https://github.com/sean1093/menpai/blob/2a5923e5de751e24586901082a7df80653e7a96e/data/source/roads.csv)
- [Gassen-/Ortsnamenkopie: villages.csv](https://github.com/sean1093/menpai/blob/2a5923e5de751e24586901082a7df80653e7a96e/data/source/villages.csv)
- [Bezirkskopie: county.xml](https://github.com/sean1093/menpai/blob/2a5923e5de751e24586901082a7df80653e7a96e/data/source/county.xml)

Eigene Dateiprüfung:

| Datei | Eigener Befund | SHA-256 der gelesenen Kopie |
| --- | --- | --- |
| roads.csv | 30.030 Datenzeilen, 30.009 unterschiedliche chinesisch-englische Paare; zusätzlich eine Kopfzeile | `5b3a2152b61f6b49aa04e03cff4594d59fa8d5c24069e95a75b0d28a12c4cab9` |
| villages.csv | 8.369 Zeilen; darunter benannte Gassen und Verwaltungseinheiten | `629c6e29264572fb88447614b38cc100ed57f7e1d6fe54cb75ab277989d093be` |
| county.xml | 371 Einträge insgesamt, darunter zwölf Bezirke von Taipei City und 29 Bezirke von New Taipei City | `24acfe52023f0ddc2149a2f8368910cd0968584913f3ac17678abb3048cba1b9` |

Die selbst berechneten Hashes stimmen mit dem Manifest desselben Projekts überein. Die Dateien wurden außerdem über die oben genannte feste Git-Version erneut abgerufen und bytegleich bestätigt. Das belegt Reproduzierbarkeit innerhalb dieses Projekts, keine unabhängige Authentifizierung durch die Post.

## 3. Konkrete Namensbeispiele

Wörtliche Einträge aus der untersuchten Straßenkopie, keine automatisch erzeugten Umschriften. Der Originalabgleich mit der aktuellen Postdatei steht aus.

| Traditionelles Chinesisch | Englischer Eintrag |
| --- | --- |
| 東湖路 | Donghu Rd. |
| 康寧路三段 | Sec. 3, Kangning Rd. |
| 內湖路一段 | Sec. 1, Neihu Rd. |
| 大湖山莊街 | Dahu Shanzhuang St. |
| 忠孝東路四段 | Sec. 4, Zhongxiao E. Rd. |
| 羅斯福路一段 | Sec. 1, Roosevelt Rd. |
| 市民大道二段 | Sec. 2, Civic Blvd. |
| 基隆路一段 | Sec. 1, Keelung Rd. |
| 重慶北路一段 | Sec. 1, Chongqing N. Rd. |
| 廈門街 | Xiamen St. |

Das zeigt, warum pauschale automatische Pinyin-Erzeugung ungeeignet ist: Namen wie Roosevelt, Civic und Keelung müssen aus einer belegten Referenz übernommen werden. Nicht jede offizielle Schreibweise lässt sich aus einer einzigen Umschriftregel ableiten.

### Zwölf Taipei-Bezirke in der untersuchten Bezirkskopie

Die englischen Einträge enthalten im Original jeweils zusätzlich `, Taipei City`.

| Bezirk | Englischer Eintrag ohne Stadtzusatz | Postcode |
| --- | --- | --- |
| 中正區 | Zhongzheng Dist. | 100 |
| 大同區 | Datong Dist. | 103 |
| 中山區 | Zhongshan Dist. | 104 |
| 松山區 | Songshan Dist. | 105 |
| 大安區 | Da’an Dist. | 106 |
| 萬華區 | Wanhua Dist. | 108 |
| 信義區 | Xinyi Dist. | 110 |
| 士林區 | Shilin Dist. | 111 |
| 北投區 | Beitou Dist. | 112 |
| 內湖區 | Neihu Dist. | 114 |
| 南港區 | Nangang Dist. | 115 |
| 文山區 | Wenshan Dist. | 116 |

Schreibvarianten wie Apostrophformen oder Ortsnamen aus anderen Quellen werden nicht stillschweigend vereinheitlicht. Ein Abgleich mit städtischen Schreibweisen und Straßenschildern bleibt erforderlich, bevor eine verbindliche Anzeigeform festgelegt wird.

### 29 Bezirke von New Taipei City in derselben Referenzkopie

Für die Gebietserweiterung wurde die untersuchte Bezirkskopie erneut ausgewertet. Sie enthält alle 29 Bezirke von New Taipei City; die Namen konnten jeweils genau einer Fläche im dokumentierten g0v-Bestand zugeordnet werden. Die englischen Einträge enthalten im Original zusätzlich `, New Taipei City`. Die Nachweisgrenzen des Originalabgleichs bleiben dieselben.

| Traditionelles Chinesisch | Englischer Eintrag |
| --- | --- |
| 萬里區 | Wanli Dist. |
| 金山區 | Jinshan Dist. |
| 板橋區 | Banqiao Dist. |
| 汐止區 | Xizhi Dist. |
| 深坑區 | Shenkeng Dist. |
| 石碇區 | Shiding Dist. |
| 瑞芳區 | Ruifang Dist. |
| 平溪區 | Pingxi Dist. |
| 雙溪區 | Shuangxi Dist. |
| 貢寮區 | Gongliao Dist. |
| 新店區 | Xindian Dist. |
| 坪林區 | Pinglin Dist. |
| 烏來區 | Wulai Dist. |
| 永和區 | Yonghe Dist. |
| 中和區 | Zhonghe Dist. |
| 土城區 | Tucheng Dist. |
| 三峽區 | Sanxia Dist. |
| 樹林區 | Shulin Dist. |
| 鶯歌區 | Yingge Dist. |
| 三重區 | Sanchong Dist. |
| 新莊區 | Xinzhuang Dist. |
| 泰山區 | Taishan Dist. |
| 林口區 | Linkou Dist. |
| 蘆洲區 | Luzhou Dist. |
| 五股區 | Wugu Dist. |
| 八里區 | Bali Dist. |
| 淡水區 | Tamsui Dist. |
| 三芝區 | Sanzhi Dist. |
| 石門區 | Shimen Dist. |

## 4. Was diese Verzeichnisse nicht leisten

### Landesweite Namen sind keine Taipei-Straßenobjekte

`roads.csv` hat nur die Spalten `中文街路名稱` und `英文街路名稱`. Es fehlen Stadt, Bezirk, Koordinaten, Straßenverlauf und eine eindeutige Kennung der geografischen Straße. Die 30.030 Zeilen sind ausdrücklich kein Umfangsnachweis für die Straßen einer der beiden Städte.

Folge: Für jede Quizaufgabe benötigen wir zusätzlich die tatsächlich existierende Straßeneinheit in Taipei City oder New Taipei City, deren Geometrie und Bezirkszuordnung. Namen allein dürfen nicht dazu führen, gleichnamige Straßen anderer Städte einzubeziehen oder Geometrien zu erfinden.

### Sections, Lanes und Alleys

Die Kopie enthält ganze Straßen und zahlreiche ausdrücklich benannte Sections. Sie enthält auch benannte Lanes und einzelne komplexere Gassennamen. Sie ist aber kein vollständiges Verzeichnis aller nummerierten Gassen bis zur kleinsten Alley.

Eine nummerierte Lane beziehungsweise Alley benötigt daher zwei Nachweise: ihre tatsächliche Existenz und Geometrie aus einem geeigneten Bestand sowie die belegte Benennungs-/Formatierungsregel. `段`, `巷` und `弄` entsprechen in der untersuchten Referenz `Sec.`, `Ln.` und `Aly.`; damit darf man keine fehlenden Straßen oder beliebigen Nummernkombinationen erzeugen. Eine verbindliche Regel ist noch am amtlichen Werkzeug beziehungsweise dessen Dokumentation abzugleichen.

### Postalische Schreibweise und Straßenschild

Die Post ist eine konkrete Referenz für englische Adressdarstellung. Dass jeder Eintrag exakt der heutigen Beschriftung jedes Taipei-Straßenschilds entspricht, wurde nicht nachgewiesen. Bei abweichenden amtlichen Quellen brauchen wir eine dokumentierte Priorität und gegebenenfalls zusätzliche akzeptierte Schreibvarianten.

### Nutzungsrechte

Die privaten Projekte nennen MIT-Lizenzen. Das bestätigt nicht automatisch die Rechte am amtlichen Ausgangsmaterial. Vor dem Mitliefern eines vollständigen Bestands sind die Bedingungen des Postdownloads beziehungsweise eines amtlichen Open-Data-Eintrags zu prüfen. Der vorliegende Bericht enthält nur wenige Beispiele, keine neu veröffentlichte vollständige Datenkopie.

## 5. Weitere Projekte und ihre Grenzen

- [mkfsn/tw-address-translator](https://github.com/mkfsn/tw-address-translator): unabhängiger Verweis auf den Postdownload und konkrete ältere XLS/XLSX-Dateien. Hilfreich zur Quellensuche, keine amtliche Veröffentlichung.
- [donma/TaiwanAddressCityAreaRoadChineseEnglishJSON](https://github.com/donma/TaiwanAddressCityAreaRoadChineseEnglishJSON): leicht nutzbarer, nach Städten und Bezirken gegliederter Bestand. Die [selbst geprüfte Dateihistorie von AllData.json](https://github.com/donma/TaiwanAddressCityAreaRoadChineseEnglishJSON/commits/master/AllData.json) zeigt als letzten Dateicommit den 24. Februar 2016, Commit `7f9c513db4d2a91a32edeacb15c9fd5f1fe31c58`. Ein 2026 überarbeitetes README macht diesen Datenbestand nicht aktuell. Deshalb kein ungeprüfter aktueller Ausgangskatalog.
- [mlouielu/twaddress](https://github.com/mlouielu/twaddress): privater Übersetzer, keine bevorzugte Primärquelle.
- `menpai` enthält auch automatische Fallback-Umschrift für nicht gelistete Namen. Deren Ausgabe ist ausdrücklich nicht gleichbedeutend mit einem amtlich belegten Namen; die Bibliothek wurde weder installiert noch als App-Abhängigkeit gewählt.

## 6. Konsequenz für die App-Planung

1. Postverzeichnisse als bevorzugten Kandidaten für die bilinguale Namensreferenz prüfen und nach Originaldownload mit Ausgabestand und Lizenz dokumentieren.
2. Einen geeigneten Geodatenbestand für beide Städte für Existenz, Sections, Lanes, Alleys, Bezirke und Straßenverläufe getrennt beschaffen. OSM bleibt dafür ein Kandidat, keine bewiesene vollständige Abdeckung.
3. Namen anhand der chinesischen Straßeneinheit und ihres geografischen Kontexts zuordnen. Originalnamen erhalten; Normalisierung nur als zusätzlicher Such-/Abgleichsschlüssel.
4. Fehlende oder widersprüchliche englische Namen als ungeklärt kennzeichnen, keine generierten Umschriften als amtlich ausgeben.
5. Vor einer vollständigen Quizfreigabe Abdeckung und Sonderfälle prüfen. Die bisher bestätigte Anforderung „alle Straßengrößen“ wird durch die Datenlücken nicht stillschweigend reduziert.
6. Nach Rechte- und Datenprüfung lokal nutzbare Dateien vorbereiten. Das Namensverzeichnis benötigt keine dauerhafte kostenpflichtige Übersetzungs-API; Gebührenfreiheit und Bereitstellungsrechte bleiben vor der Übernahme zu belegen.

## Recherchegrenzen und nächster notwendiger Nachweis

Die vertiefte Recherche nutzte öffentlich erreichbare GitHub-Suche, Original-READMEs verschiedener Projekte, feste Dateiabrufe, eigene CSV-/XML-Auswertung und die Dateihistorie eines älteren Bestands. Spätere Suchanfragen wurden von GitHub mit HTTP 429 begrenzt; die Suche wurde daraufhin nicht unverändert wiederholt.

Der Zugriff auf die amtlichen Domains wurde tatsächlich versucht und vom Cloud-Proxy mit HTTP 403 blockiert. Die Domainanforderungen `www.post.gov.tw`, `data.gov.tw` und `english.gov.taipei` wurden zusätzlich zu den bestehenden Domains im Konfigurationsentwurf gespeichert. Das aktiviert die Freigaben nicht und ist keine Veröffentlichung; der letzte Speichervorgang meldete weiterhin `requires_publish: true`.

Der entscheidende noch fehlende Schritt ist der direkte Abruf der aktuellen Postdateien und ihrer Nutzungsbedingungen sowie die Prüfung eines passenden Taipei-Geodatenbestands. Dieser Bericht behauptet weder eine vollständige freie Websuche noch eine abgeschlossene amtliche Verifikation. Die Namensrecherche selbst hat keinen Anwendungscode erstellt; die danach begonnene Bezirksumsetzung ist in [README.md](README.md) separat beschrieben und ist keine zusätzliche amtliche Datenverifikation.
