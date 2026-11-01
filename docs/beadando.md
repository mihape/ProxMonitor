# Szakmai Beadandó Dolgozat

> **Intézmény:** Miskolci Egyetem – Gépészmérnöki és Informatikai Kar  
> **Tantárgy:** Mobilprogramozás  
> **Témakör:** REST API és JSON-feldolgozás Android-alkalmazásokban  
> **Projekt:** ProxMonitor  
> **Készítette:** Mihalek Péter  

---

## 1. Bevezetés és a választott téma indoklása

A modern mobilalkalmazások döntő többsége nem izolált szigetként működik, hanem hálózaton keresztül, központi szerverekkel vagy felhőszolgáltatásokkal kommunikál. Az elosztott rendszerek közötti kommunikáció legelterjedtebb iparági szabványa a **REST (Representational State Transfer)** architektúra, míg az adatok átvitelére és szerializálására a könnyűsúlyú **JSON (JavaScript Object Notation)** formátum a domináns választás.

A dolgozat és a hozzá tartozó **ProxMonitor** projekt célja a RESTful API-k Android környezetben történő professzionális kezelésének, az aszinkron hálózati műveleteknek és a strukturált JSON adatok deszerializációjának gyakorlati bemutatása egy valós idejű rendszermonitorozó alkalmazás megvalósításán keresztül.

---

## 2. A megoldott probléma: Proxmox VE infrastruktúra-felügyelet

A Proxmox Virtual Environment (PVE) egy nyílt forráskódú, vállalati szintű szerver-virtualizációs platform. Bár a Proxmox fejlett webes kezelőfelülettel rendelkezik, az asztali böngészőre tervezett felület okostelefonon nehezen kezelhető, és nem nyújt gyors, egypillantásos áttekintést.

A fejlesztett rendszer lehetővé teszi, hogy a rendszergazda:
- másodpercek alatt ellenőrizhesse a szerver pillanatnyi processzor-, memória- és lemezterhelését,
- nyomon kövesse a kritikus virtuális gépek (VM) és konténerek (LXC) futási állapotát,
- biztonságos csatornán keresztül, a legkisebb jogosultság elve mellett férjen hozzá a statisztikákhoz.

---

## 3. Felhasznált technológiák és szakmai döntések

### 3.1. Kliensoldal: Modern Android fejlesztés
1. **Kotlin nyelv:**
   - Teljes típusbiztonság és null-safety (`?` operátor), amellyel elkerülhető a hálózati JSON feldolgozáskor leggyakrabban előforduló hiba, a `NullPointerException`.
   - Adatosztályok (`data class`) a REST API válaszok tiszta, tömör modellezésére.

2. **Jetpack Compose UI keretrendszer:**
   - A hagyományos XML-alapú nézetekkel (Views/Layouts) szemben a Compose deklaratív szemléletű: a felület egy állapotfüggvény (`UI = f(State)`).
   - Recomposition mechanizmus: ha a hálózatból új mérési adat érkezik, kizárólag azok a komponensek frissülnek a képernyőn, amelyek adata megváltozott.

3. **Material 3 tervezési irányelvek:**
   - Kártya alapú elrendezés (`Card`, `StatCard`, `ServerCard`), lekerekített sarkok és konzisztens sötét téma, amely ideális a műszerfal típusú monitorozáshoz.

### 3.2. Szerveroldal és Biztonság: FastAPI Backend
- A mobilalkalmazás és a Proxmox közé egy dedikált Python FastAPI köztes réteg került beépítésre.
- **Biztonsági megfontolás:** A Proxmox API token soha nem juthat el a mobiltelefonra, mivel a telefonos környezet nem tekinthető megbízható titoktárolónak. A köztes backend elrejti a hitelesítést, és kizárólag szűrt, tiszta JSON választ szolgáltat a mobilnak.

---

## 4. A megvalósítás jelenlegi állapota (v0.1.0 mérföldkő)

A projekt első fejlesztési fázisában (v0.1.0):
1. Elkészült a stabil, deklaratív **Jetpack Compose kezdőképernyő** (`DashboardScreen`), amely a fizikai telefonon és az emulátorban is sikeresen renderelődik.
2. Megvalósításra kerültek az önálló, újrahasznosítható UI komponensek:
   - `StatCard`: Erőforrás-mutatók (CPU, RAM, Tárhely) kiemelése színekkel és tipográfiával.
   - `ServerCard`: Szerverállapot (futó entitások neve, típusa, státusza) strukturált megjelenítése.
3. Kialakításra került a teljes Gradle projektstruktúra a Gradle Wrapperrel és szigorú `.gitignore` konfigurációval.
4. Rögzítésre kerültek az API specifikációk és az architektúra tervei a további fázisokhoz.

---

## 5. Következő fejlesztési lépések
A projekt következő lépéseiben a FastAPI backend (v0.2.0) megvalósítása és a Retrofit 2 REST kliens beépítése (v0.3.0) fog megtörténni, amellyel a jelenlegi mintaadatokat élő szervermetrikák váltják fel.
