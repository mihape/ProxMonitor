package hu.petermihalek.proxmonitor.network

import java.net.URI
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

/**
 * Egyszerű Singleton objektum a Retrofit példányosításához és eléréséhez.
 */
object RetrofitInstance {

    /**
     * Az API alapértelmezett címe:
     * - Android Emulátorban: "http://10.0.2.2:8000/" (ezzel éri el a gép localhostját)
     * - Távoli/éles környezetben: HTTPS alapú végpont (pl. "https://proxmonitor.pelda.hu/")
     */
    @Volatile
    var baseUrl: String = "http://10.0.2.2:8000/"
        private set

    private var retrofit: Retrofit? = null

    @Synchronized
    fun getApi(): ApiService {
        val currentRetrofit = retrofit ?: buildRetrofit(baseUrl).also { retrofit = it }
        return currentRetrofit.create(ApiService::class.java)
    }

    /**
     * Ellenőrzi és normalizálja a megadott szerver URL-t.
     * Helyi fejlesztői címeknél (10.0.2.2, 127.0.0.1, localhost) alapértelmezetten 'http://',
     * minden egyéb séma nélküli címnél biztonságos 'https://' előtagot alkalmaz,
     * valamint pótolja a lezáró '/' karaktert.
     *
     * @throws IllegalArgumentException ha az URL üres vagy szintaktikailag érvénytelen.
     */
    fun normalizeBaseUrl(newUrl: String): String {
        var sanitized = newUrl.trim()
        if (sanitized.isEmpty()) {
            throw IllegalArgumentException("A szerver URL nem lehet üres.")
        }
        if (sanitized.any { it.isWhitespace() }) {
            throw IllegalArgumentException("A szerver URL nem tartalmazhat szóközt.")
        }

        val lower = sanitized.lowercase()
        sanitized = when {
            lower.startsWith("http://") -> "http://" + sanitized.substring(7)
            lower.startsWith("https://") -> "https://" + sanitized.substring(8)
            lower.contains("://") -> {
                throw IllegalArgumentException("Csak http:// vagy https:// protokoll támogatott.")
            }
            isLocalDevAddress(lower) -> "http://$sanitized"
            else -> "https://$sanitized"
        }

        if (!sanitized.endsWith("/")) {
            sanitized = "$sanitized/"
        }

        val uri = try {
            URI(sanitized)
        } catch (e: Exception) {
            throw IllegalArgumentException("Érvénytelen URL formátum: $newUrl", e)
        }

        val host = uri.host
        if (host.isNullOrBlank()) {
            throw IllegalArgumentException("Hiányzó vagy érvénytelen szervernév / IP-cím: $newUrl")
        }
        if (uri.port !in -1..65535 || uri.port == 0) {
            throw IllegalArgumentException("Érvénytelen portszám az URL-ben: $newUrl")
        }

        return sanitized
    }

    /**
     * Lehetővé teszi a szervercím futásidejű, biztonságos módosítását.
     * Hibás URL esetén [IllegalArgumentException]-t dob, és nem rontja el a meglévő példányt.
     */
    @Synchronized
    fun updateBaseUrl(newUrl: String): String {
        val normalized = normalizeBaseUrl(newUrl)
        val newRetrofit = buildRetrofit(normalized)
        baseUrl = normalized
        retrofit = newRetrofit
        return normalized
    }

    private fun buildRetrofit(url: String): Retrofit {
        return try {
            Retrofit.Builder()
                .baseUrl(url)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
        } catch (e: Exception) {
            throw IllegalArgumentException("Érvénytelen szerver URL: $url", e)
        }
    }

    private fun isLocalDevAddress(addressWithoutScheme: String): Boolean {
        val hostPart = addressWithoutScheme.substringBefore("/").substringBefore(":")
        return hostPart == "10.0.2.2" || hostPart == "127.0.0.1" || hostPart == "localhost"
    }
}
