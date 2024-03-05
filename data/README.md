# JourneyBench Network Data

JourneyBench comes with 5 preprocessed networks. These networks are generated from public GTFS feeds and OpenStreetMap data. The table below shows which data was used to generate each network.

| Network               | Location        | Transit Source                                                                                | Footpaths Source                                                                      | Shape Source                                                                      |
|:----------------------|:----------------|:----------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|
| `berlin.network`      | Berlin          | [daten.berlin.de](https://daten.berlin.de/datensaetze/vbb-fahrplandaten-gtfs)                 | [download.geofabrik.de](https://download.geofabrik.de/europe/germany/berlin.html)     | [download.geofabrik.de](https://download.geofabrik.de/europe/germany/berlin.html) |
| `newyork.network`     | New York City   | [mta.info](https://new.mta.info/developers)                                                   | [download.geofabrik.de](https://download.geofabrik.de/north-america/us/new-york.html) | [polygons.openstreetmap.fr](https://polygons.openstreetmap.fr/?id=175905)         |
| `netherlands.network` | The Netherlands | [nt.ndw.nu](https://nt.ndw.nu/#/settings/multimodaal-reisinformatie-overview/1)               | [download.geofabrik.de](https://download.geofabrik.de/europe/netherlands.html)        | [download.geofabrik.de](https://download.geofabrik.de/europe/netherlands.html)    |
| `switzerland.network` | Switzerland     | [opentransportdata.swiss](https://opentransportdata.swiss/en/dataset/timetable-2023-gtfs2020) | [download.geofabrik.de](https://download.geofabrik.de/europe/switzerland.html)        | [download.geofabrik.de](https://download.geofabrik.de/europe/switzerland.html)    |
| `germany.network`     | Germany         | [gtfs.de](https://gtfs.de/en/feeds/de_full/)                                                  | [download.geofabrik.de](https://download.geofabrik.de/europe/germany.html)            | [download.geofabrik.de](https://download.geofabrik.de/europe/germany.html)        |

The sizes of the networks, as they appear in this directory, are shown in the table below.

| Network               | Date       | Days |  Stops |   Trips | Connections |   Nodes |    Paths |
|:----------------------|:-----------|-----:|-------:|--------:|------------:|--------:|---------:|
| `berlin.network`      | 2024-04-26 |    2 |  15948 |   79381 |     1804809 |  268959 |   432612 |
| `newyork.network`     | 2024-01-08 |    2 |  15948 |  127570 |     4229485 |  285254 |   486973 |
| `netherlands.network` | 2024-01-19 |    2 |  42675 |  187516 |     3043477 | 1349756 |  2084791 |
| `switzerland.network` | 2023-08-23 |    2 |  28228 |  637064 |     5578108 |  955320 |  1474934 |
| `germany.network`     | 2024-01-12 |    2 | 375185 | 1205428 |    23701605 | 9255833 | 14266475 |

It is possible to use the networks without JourneyBench, the structure of the `.network` file format is described in the Protobuf file at `protobuf/network.proto`. Note that the `.network` files are compressed using the gzip compression algorithm to reduce the filesize.

Network files are tracked in this repository using [Git Large File Storage](https://git-lfs.com/).
