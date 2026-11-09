package hu.petermihalek.proxmonitor

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import hu.petermihalek.proxmonitor.network.ResourceItem
import hu.petermihalek.proxmonitor.network.ServerStatusResponse
import hu.petermihalek.proxmonitor.ui.theme.ProxMonitorTheme

class MainActivity : ComponentActivity() {

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    setContent {
      ProxMonitorTheme {
        val viewModel: MainViewModel = viewModel()
        DashboardScreen(viewModel)
      }
    }
  }
}

@Composable
fun DashboardScreen(viewModel: MainViewModel) {

  val backgroundColor = Color(0xFF0B1220)
  val textColor = Color.White
  val uiState by viewModel.uiState.collectAsState()

  var showSettingsDialog by remember { mutableStateOf(false) }

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
    ) {

      // FEJLÉC: Cím, állapotjelző és gombok
      Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
      ) {
        Column {
          Text(
            text = "ProxMonitor",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = textColor
          )

          Text(
            text = "Proxmox szerver vezérlőpult",
            fontSize = 13.sp,
            color = Color.Gray
          )
        }

        Row(
          horizontalArrangement = Arrangement.spacedBy(4.dp),
          verticalAlignment = Alignment.CenterVertically
        ) {
          // Beállítások gomb (Szerver IP és API kulcs megadása)
          TextButton(
            onClick = { showSettingsDialog = true }
          ) {
            Text("⚙", fontSize = 18.sp, color = Color.LightGray)
          }

          // Frissítés gomb
          Button(
            onClick = { viewModel.loadData() },
            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E293B))
          ) {
            Text("Frissítés", fontSize = 13.sp, color = Color(0xFF38BDF8))
          }
        }
      }

      // ÜZEMMÓD BADGE (Élő mód vagy Bemutató mód)
      when (val state = uiState) {
        is UiState.Success -> {
          val isLive = state.status.mode.equals("LIVE", ignoreCase = true)
          val badgeBg = if (isLive) Color(0xFF0E3321) else Color(0xFF2E2415)
          val badgeTextColor = if (isLive) Color(0xFF22C55E) else Color(0xFFF59E0B)
          val badgeText = if (isLive) "● Élő kapcsolat: ${state.status.node_name}" else "● Bemutató mód (DEMO)"

          Box(
            modifier = Modifier
              .background(badgeBg, RoundedCornerShape(8.dp))
              .padding(horizontal = 12.dp, vertical = 6.dp)
          ) {
            Text(
              text = badgeText,
              fontSize = 12.sp,
              fontWeight = FontWeight.SemiBold,
              color = badgeTextColor
            )
          }
        }
        else -> {}
      }

      Spacer(modifier = Modifier.height(4.dp))

      // ÁLLAPOTFÜGGŐ TARTALOM (Loading, Error, Success)
      when (val state = uiState) {
        is UiState.Loading -> {
          Box(
            modifier = Modifier
              .fillMaxWidth()
              .height(300.dp),
            contentAlignment = Alignment.Center
          ) {
            Column(
              horizontalAlignment = Alignment.CenterHorizontally,
              verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
              CircularProgressIndicator(color = Color(0xFF3B82F6))
              Text(
                text = "Szerveradatok lekérdezése a REST API-ról...",
                color = Color.LightGray,
                fontSize = 14.sp
              )
            }
          }
        }

        is UiState.Error -> {
          Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF2A1515))
          ) {
            Column(
              modifier = Modifier.padding(20.dp),
              verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
              Text(
                text = "Hiba történt a lekérdezéskor",
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp,
                color = Color(0xFFEF4444)
              )

              Text(
                text = state.message,
                color = Color.LightGray,
                fontSize = 14.sp
              )

              Button(
                onClick = { viewModel.loadData() },
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFEF4444)),
                modifier = Modifier.align(Alignment.End)
              ) {
                Text("Újrapróbálkozás")
              }
            }
          }
        }

        is UiState.Success -> {
          SuccessContent(state.status, state.resources)
        }
      }
    }
  }

  // BEÁLLÍTÁSOK PÁRBESZÉDABLAK (IP cím és API kulcs)
  if (showSettingsDialog) {
    SettingsDialog(
      currentUrl = viewModel.serverUrl,
      currentApiKey = viewModel.apiKey,
      onDismiss = { showSettingsDialog = false },
      onSave = { newUrl, newKey ->
        viewModel.updateSettings(newUrl, newKey)
        showSettingsDialog = false
      }
    )
  }
}

@Composable
fun SuccessContent(
  status: ServerStatusResponse,
  resources: List<ResourceItem>
) {
  val textColor = Color.White

  Text(
    text = "Szerver állapota",
    fontSize = 20.sp,
    fontWeight = FontWeight.Bold,
    color = textColor
  )

  StatCard(
    title = "CPU terhelés (${status.cpu.cores} mag)",
    value = "${status.cpu.usage_percent}%",
    color = Color(0xFF3B82F6)
  )

  StatCard(
    title = "Memóriahasználat (${status.memory.usage_percent}%)",
    value = status.memory.formatted,
    color = Color(0xFF22C55E)
  )

  StatCard(
    title = "Tárhely (${status.storage.usage_percent}%)",
    value = status.storage.formatted,
    color = Color(0xFFF59E0B)
  )

  StatCard(
    title = "Szerver üzemidő",
    value = status.uptime_formatted,
    color = Color(0xFFA855F7)
  )

  Spacer(modifier = Modifier.height(12.dp))

  Text(
    text = "Virtuális gépek és konténerek (${resources.size} db)",
    fontSize = 20.sp,
    fontWeight = FontWeight.Bold,
    color = textColor
  )

  if (resources.isEmpty()) {
    Text(
      text = "Nincsenek elérhető virtuális gépek ezen a szerveren.",
      color = Color.Gray,
      fontSize = 14.sp
    )
  } else {
    resources.forEach { item ->
      ServerCard(
        name = item.name,
        type = "${item.type} (${item.vmid})",
        status = item.display_status,
        memory = item.memory_formatted
      )
    }
  }
}

@Composable
fun StatCard(
  title: String,
  value: String,
  color: Color
) {
  Card(
    modifier = Modifier.fillMaxWidth(),
    shape = RoundedCornerShape(16.dp),
    colors = CardDefaults.cardColors(containerColor = Color(0xFF182235))
  ) {
    Column(
      modifier = Modifier.padding(18.dp),
      verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
      Text(
        text = title,
        color = Color.LightGray,
        fontSize = 13.sp
      )

      Text(
        text = value,
        color = color,
        fontSize = 24.sp,
        fontWeight = FontWeight.Bold
      )
    }
  }
}

@Composable
fun ServerCard(
  name: String,
  type: String,
  status: String,
  memory: String? = null
) {
  val isOnline = status.equals("Online", ignoreCase = true) || status.equals("running", ignoreCase = true)
  val statusColor = if (isOnline) Color(0xFF22C55E) else Color(0xFF94A3B8)

  Card(
    modifier = Modifier.fillMaxWidth(),
    shape = RoundedCornerShape(12.dp),
    colors = CardDefaults.cardColors(containerColor = Color(0xFF182235))
  ) {
    Row(
      modifier = Modifier
        .fillMaxWidth()
        .padding(16.dp),
      horizontalArrangement = Arrangement.SpaceBetween,
      verticalAlignment = Alignment.CenterVertically
    ) {
      Column {
        Text(
          text = name,
          color = Color.White,
          fontWeight = FontWeight.Bold,
          fontSize = 15.sp
        )

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
          Text(
            text = type,
            color = Color.Gray,
            fontSize = 12.sp
          )
          if (!memory.isNullOrEmpty()) {
            Text(
              text = "•  $memory",
              color = Color.Gray,
              fontSize = 12.sp
            )
          }
        }
      }

      Text(
        text = status,
        color = statusColor,
        fontWeight = FontWeight.Bold,
        fontSize = 14.sp
      )
    }
  }
}

@Composable
fun SettingsDialog(
  currentUrl: String,
  currentApiKey: String,
  onDismiss: () -> Unit,
  onSave: (String, String) -> Unit
) {
  var urlText by remember { mutableStateOf(currentUrl) }
  var keyText by remember { mutableStateOf(currentApiKey) }

  AlertDialog(
    onDismissRequest = onDismiss,
    title = { Text("Kapcsolati beállítások") },
    text = {
      Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
          text = "Emulátorhoz: http://10.0.2.2:8000/\nFizikai telefonhoz a PC helyi IP címe szükséges (pl. http://192.168.1.50:8000/).",
          fontSize = 12.sp,
          color = Color.Gray
        )

        OutlinedTextField(
          value = urlText,
          onValueChange = { urlText = it },
          label = { Text("Backend URL") },
          singleLine = true
        )

        OutlinedTextField(
          value = keyText,
          onValueChange = { keyText = it },
          label = { Text("API Kulcs (X-API-Key)") },
          singleLine = true
        )
      }
    },
    confirmButton = {
      Button(onClick = { onSave(urlText, keyText) }) {
        Text("Mentés és Frissítés")
      }
    },
    dismissButton = {
      TextButton(onClick = onDismiss) {
        Text("Mégse")
      }
    }
  )
}
