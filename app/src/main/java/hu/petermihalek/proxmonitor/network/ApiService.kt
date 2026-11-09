package hu.petermihalek.proxmonitor.network

import retrofit2.http.GET
import retrofit2.http.Header

/**
 * Retrofit interfész a REST API végpontok meghívásához.
 * A metódusok 'suspend' kulcsszóval vannak ellátva, hogy Coroutine-ból lehessen őket hívni.
 */
interface ApiService {

    @GET("api/v1/status")
    suspend fun getServerStatus(
        @Header("X-API-Key") apiKey: String
    ): ServerStatusResponse

    @GET("api/v1/resources")
    suspend fun getResources(
        @Header("X-API-Key") apiKey: String
    ): ResourcesResponse
}
