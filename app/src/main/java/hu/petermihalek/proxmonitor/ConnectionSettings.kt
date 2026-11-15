package hu.petermihalek.proxmonitor

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import hu.petermihalek.proxmonitor.network.RetrofitInstance
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/** A backend URL és API-kulcs mentése, illetve visszaolvasása. */
data class ConnectionSettings(val backendUrl: String, val apiKey: String)

interface ConnectionSettingsRepository {
    fun read(): ConnectionSettings
    fun write(settings: ConnectionSettings)
}

/** A kulcs titkosítása Android Keystore-ban védett AES-kulccsal történik. */
class SecureConnectionSettings(context: Context) : ConnectionSettingsRepository {
    private val prefs = context.applicationContext.getSharedPreferences(PREFS_FILE, Context.MODE_PRIVATE)

    override fun read(): ConnectionSettings {
        val url = prefs.getString(URL_KEY, RetrofitInstance.baseUrl) ?: RetrofitInstance.baseUrl
        val encryptedKey = prefs.getString(API_KEY, null)
        val key = if (encryptedKey == null) {
            ""
        } else {
            try {
                decrypt(encryptedKey)
            } catch (_: Exception) {
                // Pl. sérült adat vagy más eszközről visszaállított kulcs: újból meg kell adni.
                ""
            }
        }
        return ConnectionSettings(url, key)
    }

    override fun write(settings: ConnectionSettings) {
        val encryptedKey = encrypt(settings.apiKey)
        val saved = prefs.edit()
            .putString(URL_KEY, settings.backendUrl)
            .putString(API_KEY, encryptedKey)
            .commit()
        if (!saved) throw IllegalStateException("Nem sikerült elmenteni a beállításokat.")
    }

    private fun encrypt(plaintext: String): String {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey())
        val iv = Base64.encodeToString(cipher.iv, Base64.NO_WRAP)
        val ciphertext = Base64.encodeToString(
            cipher.doFinal(plaintext.toByteArray(Charsets.UTF_8)), Base64.NO_WRAP
        )
        return "$iv:$ciphertext"
    }

    private fun decrypt(stored: String): String {
        val parts = stored.split(':', limit = 2)
        require(parts.size == 2) { "Hibásan tárolt hitelesítési adat." }
        val iv = Base64.decode(parts[0], Base64.NO_WRAP)
        val ciphertext = Base64.decode(parts[1], Base64.NO_WRAP)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, secretKey(), GCMParameterSpec(128, iv))
        return String(cipher.doFinal(ciphertext), Charsets.UTF_8)
    }

    private fun secretKey(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val existing = keyStore.getKey(KEY_ALIAS, null) as? SecretKey
        if (existing != null) return existing

        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        generator.init(
            KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .build()
        )
        return generator.generateKey()
    }

    private companion object {
        const val PREFS_FILE = "proxmonitor_connection_settings"
        const val URL_KEY = "backend_url"
        const val API_KEY = "api_key_encrypted"
        const val KEY_ALIAS = "proxmonitor_settings_aes_v1"
    }
}
