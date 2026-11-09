package hu.petermihalek.proxmonitor.network

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

/**
 * Egyszerű Singleton objektum a Retrofit példányosításához és eléréséhez.
 */
object RetrofitInstance {

    /**
     * Az API alapértelmezett címe:
     * - Android Emulátorban: "http://10.0.2.2:8000/" (ezzel éri el a gép localhostját)
     * - Fizikai telefonon: A számítógép helyi Wi-Fi IP-címe (pl. "http://192.168.1.150:8000/")
     */
    var baseUrl: String = "http://10.0.2.2:8000/"

    private var retrofit: Retrofit? = null

    fun getApi(): ApiService {
        if (retrofit == null) {
            retrofit = Retrofit.Builder()
                .baseUrl(baseUrl)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
        }
        return retrofit!!.create(ApiService::class.java)
    }

    /**
     * Lehetővé teszi az IP-cím futásidejű módosítását (ha fizikai telefonon tesztelsz).
     */
    fun updateBaseUrl(newUrl: String) {
        val sanitized = if (newUrl.endsWith("/")) newUrl else "$newUrl/"
        baseUrl = sanitized
        retrofit = null // Újrainicializálja az új címmel
    }
}
