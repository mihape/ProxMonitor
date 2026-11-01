# Szóbeli Védési Útmutató és Vizsgafelkészítő

Ez a dokumentum a **Mobilprogramozás** tantárgyi beadandó szóbeli védésére való felkészülést szolgálja. Lépésről lépésre bemutatja az alkalmazás működését, a forráskód részleteit, valamint összegyűjti a várható oktatói kérdéseket precíz, szakmai mintaválaszokkal.

---

## 1. A megvalósított Android forráskód részletes magyarázata

A jelenlegi verzióban (v0.1.0) a teljes felhasználói felület a `MainActivity.kt` fájlban található Jetpack Compose technológiával készült.

### 1.1. `MainActivity` és a felület inicializálása
```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ProxMonitorTheme {
                DashboardScreen()
            }
        }
    }
}
```
- **`ComponentActivity`:** A modern Android-alkalmazások alapvető Activity ősosztálya, amely támogatja a Jetpack Compose-t és a legújabb Android életciklus-kezelést.
- **`onCreate()`:** Az Activity életciklusának első állomása, amely akkor fut le, amikor az operációs rendszer példányosítja az ablakot.
- **`setContent {}`:** A hagyományos `setContentView(R.layout.activity_main)` helyett használt függvény. Itt kapcsoljuk össze az Activity-t a Compose deklaratív függvényeivel; a blokkon belül közvetlenül `@Composable` függvényeket hívhatunk meg.
- **`ProxMonitorTheme`:** Az alkalmazás Material 3 témakörnyezete, amely a színeket, tipográfiát és alakzatokat biztosítja.

---

### 1.2. A főképernyő: `DashboardScreen()`
```kotlin
@Composable
fun DashboardScreen() {
    val backgroundColor = Color(0xFF0B1220) // Sötétkék/fekete háttér
    val textColor = Color.White

    Scaffold(
        containerColor = backgroundColor
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) { ... }
    }
}
```
- **`@Composable` annotáció:** Jelzi a Kotlin fordító számára, hogy ez a függvény adatokat alakít át vizuális felhasználói felületté (UI elem).
- **`Scaffold`:** A Material Design alapvető elrendezési váza. Automatikusan kiszámolja a rendszer sávok (státuszbár, navigációs sáv) által igényelt margót (`innerPadding`), elkerülve, hogy a tartalom a rendszerelemek mögé lógjon.
- **`Column` és `Modifier`:**
  - `fillMaxSize()`: Kitölti a teljes rendelkezésre álló képernyőterületet.
  - `verticalScroll(rememberScrollState())`: Függőleges görgethetőséget biztosít, így kisebb képernyőjű telefonokon sem vágódik le a tartalom alja.
  - `spacedBy(16.dp)`: Automatikusan 16 dp térközt tart a függőlegesen egymás alá helyezett kártyák között.

---

### 1.3. Újrahasznosítható kártya komponensek: `StatCard` és `ServerCard`
A kód modularitását és tisztaságát (DRY - Don't Repeat Yourself elv) az újrahasznosítható kis komponensek biztosítják.

1. **`StatCard` (Hardveres erőforrás kártya):**
   - Paraméterek: `title: String`, `value: String`, `color: Color`.
   - `Card(shape = RoundedCornerShape(16.dp))`: Lekerekített sarkú, sötétszürke kártya konténer.
   - Különböző kiemelő színeket használunk: Kék (CPU), Zöld (Memória), Sárga (Tárhely) a jobb áttekinthetőségért.

2. **`ServerCard` (Virtuális gép / konténer kártya):**
   - Paraméterek: `name: String`, `type: String`, `status: String`.
   - `Row(horizontalArrangement = Arrangement.SpaceBetween)`: Vízszintes elrendezés, ahol a bal oldalon a név és típus, a jobb szélen a zöld színű "Online" státusz jelenik meg.

---

## 2. Kulcsfogalmak és vizsgakérdések szakmai válaszokkal

### 1. Kérdés: Mi az a REST API és mik a legfőbb jellemzői?
> **Válasz:** A REST (Representational State Transfer) egy elosztott rendszerekhez tervezett építészeti stílus. Alapelvei:
> - **Kliens-szerver szétválasztás:** A felület és az adatkezelés független.
> - **Állapotmentesség (Statelessness):** Minden egyes HTTP-kérés tartalmazza az összes szükséges információt a feldolgozáshoz; a szerver nem tárol munkamenet-állapotot (session) a kérések között.
> - **Egységes felület (Uniform Interface):** Szabványos HTTP metódusokat használ (GET az olvasásra, POST a létrehozásra, PUT/PATCH a módosításra, DELETE a törlésre) és URL-ekkel azonosítja az erőforrásokat.
> - **Szabványos adatformátum:** Tipikusan JSON formátumban küldi és fogadja az adatokat.

---

### 2. Kérdés: Mi a JSON és hogyan dolgozza fel a Kotlin?
> **Válasz:** A JSON (JavaScript Object Notation) egy szöveges, ember által olvasható és platformfüggetlen adatcsere-formátum, amely kulcs-érték párokból és listákból épül fel.  
> A Kotlinban a JSON deszerializáció úgy történik, hogy a beérkező szöveges JSON adatot egy konverter könyvtár (pl. Gson vagy Kotlinx Serialization) a mezőnevek egyeztetésével automatikusan leképezi egy típusbiztos Kotlin `data class` példányává.

---

### 3. Kérdés: Miért Retrofit-et használunk OkHttp-vel és nem natív `HttpURLConnection`-t?
> **Válasz:** 
> - A natív `HttpURLConnection` alacsony szintű, sok hibalehetőséggel járó boilerplate (sablon) kódot igényelne a szálkezeléshez, fejlécekhez és hibakezeléshez.
> - A **Retrofit** egy deklaratív, magas szintű HTTP-kliens: az API végpontokat egyszerű Kotlin interfész metódusokként és annotációkként (`@GET`, `@Query`) definiálhatjuk.
> - Az **OkHttp** felel a megbízható hálózati kapcsolatért: támogatja a kapcsolat-újrahasznosítást (connection pooling), a HTTP/2 protokollt, a gyorsítótárazást és az interceptorokat (naplózás, hitelesítő fejlécek automatikus hozzáadása).
> - Közvetlen integrációja van a **Kotlin Coroutines**-szal, így a hálózati hívások aszinkron módon, a fő szál (Main UI Thread) blokkolása nélkül futnak le.

---

### 4. Kérdés: Hogyan működik a Jetpack Compose a korábbi XML alapú nézetekhez képest?
> **Válasz:** 
> - Az XML alapú rendszer **imperatív**: az Activity kézzel módosította a nézetek belső állapotát (`findViewById()`, `textView.setText(...)`).
> - A Jetpack Compose **deklaratív**: a felületet sima Kotlin függvényekként írjuk le, és azt mondjuk meg, hogyan nézzen ki a UI egy adott pillanatnyi állapot (State) esetén: `UI = f(State)`.
> - Amikor az állapot megváltozik (pl. megérkezik a friss CPU adat), a Compose lefolytatja a **Recomposition** folyamatot, vagyis újra meghívja azokat a Composable függvényeket, amelyek az adott adattól függenek, miközben a változatlan elemeket nem rajzolja újra.

---

### 5. Kérdés: Miért van szükség köztes Python backendre a Proxmox és az Android között?
> **Válasz:**
> 1. **Hitelesítési biztonság:** A Proxmox API-hoz szükséges titkos API tokent nem szabad a mobilkliensen tárolni, mert az APK fájlból kinyerhető. A Python backend szerveroldalon, védett környezeti változóban tárolja a tokent.
> 2. **Adatminimalizálás:** A Proxmox natív válasza több száz mezőt tartalmaz. A köztes réteg ezt leszűri kizárólag a mobil számára lényeges 4-5 adatra, kímélve a mobil sávszélességet és akkumulátort.
> 3. **Hálózati izoláció:** A Proxmox adminisztrációs portja nem kerül közvetlenül az internetre.

---

### 6. Kérdés: Mi történik, ha a szerver nem elérhető vagy hálózati hiba lép fel?
> **Válasz:** 
> A Retrofit hívást Coroutine környezetben, hibakezelő blokkban (`try-catch`) vagy egy eredménycsomagoló típusban (`Result<T>`) hajtjuk végre.
> - Hiba esetén az alkalmazás nem omlik össze (nincs `Crash`).
> - A ViewModel egy `Error` állapotba váltja a képernyőt.
> - A Jetpack Compose felületen a felhasználóbarát hibaüzenet (pl. „A szerver nem érhető el”) és egy „Újrapróbálkozás” gomb jelenik meg.

---

## 3. A működés bemutatásának menete a védésen

1. **Bevezetés (1 perc):** A projekt célja, a 3-rétegű architektúra (Android - FastAPI - Proxmox) felvázolása.
2. **Alkalmazás bemutatása élőben (2 perc):**
   - Az alkalmazás megnyitása emulátoron vagy fizikai telefonon.
   - A műszerfal bemutatása: CPU, RAM, tárhely kártyák és a virtuális környezetek állapota.
3. **Kódszerkezet ismertetése (2 perc):**
   - A `MainActivity.kt` bemutatása: `Scaffold`, `Column`, `StatCard` és `ServerCard` logikája.
   - Annak magyarázata, hogy miért és hogyan fog a Retrofit és ViewModel csatlakozni ehhez a felülethez a következő mérföldkőben.
4. **Kérdések megválaszolása:** A fenti vizsgakérdések alapján a technológiai döntések indoklása.
