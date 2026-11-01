
package hu.petermihalek.proxmonitor

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import hu.petermihalek.proxmonitor.ui.theme.ProxMonitorTheme

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

@Composable
fun DashboardScreen() {

  val backgroundColor = Color(0xFF0B1220)
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
    ) {

      Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
      ) {
        Column {
          Text(
            text = "ProxMonitor",
            fontSize = 30.sp,
            fontWeight = FontWeight.Bold,
            color = textColor
          )

          Text(
            text = "Proxmox szerver vezérlőpult",
            fontSize = 14.sp,
            color = Color.Gray
          )
        }

        Box(
          modifier = Modifier
            .background(Color(0xFF2E2415), RoundedCornerShape(8.dp))
            .padding(horizontal = 10.dp, vertical = 6.dp)
        ) {
          Text(
            text = "Bemutató mód",
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold,
            color = Color(0xFFF59E0B)
          )
        }
      }

      Spacer(modifier = Modifier.height(12.dp))

      Text(
        text = "Szerver állapota",
        fontSize = 20.sp,
        fontWeight = FontWeight.Bold,
        color = textColor
      )

      StatCard(
        title = "CPU terhelés",
        value = "24%",
        color = Color(0xFF3B82F6)
      )

      StatCard(
        title = "Memóriahasználat",
        value = "8.2 GB / 16 GB",
        color = Color(0xFF22C55E)
      )

      StatCard(
        title = "Tárhely",
        value = "1.8 TB / 4 TB",
        color = Color(0xFFF59E0B)
      )

      Spacer(modifier = Modifier.height(12.dp))

      Text(
        text = "Virtuális gépek és konténerek",
        fontSize = 20.sp,
        fontWeight = FontWeight.Bold,
        color = textColor
      )

      ServerCard("Home Assistant", "VM", "Online")
      ServerCard("Jellyfin", "LXC", "Online")
      ServerCard("AdGuard Home", "LXC", "Online")

      Spacer(modifier = Modifier.height(12.dp))

      Text(
        text = "Bemutató mód – mintaadatok (nincs aktív szerverkapcsolat)",
        fontSize = 12.sp,
        color = Color.Gray
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

    colors = CardDefaults.cardColors(
      containerColor = Color(0xFF182235)
    )
  ) {

    Column(
      modifier = Modifier.padding(20.dp),

      verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {

      Text(
        text = title,
        color = Color.LightGray,
        fontSize = 14.sp
      )

      Text(
        text = value,
        color = color,
        fontSize = 26.sp,
        fontWeight = FontWeight.Bold
      )
    }
  }
}

@Composable
fun ServerCard(
  name: String,
  type: String,
  status: String
) {

  Card(
    modifier = Modifier.fillMaxWidth(),

    shape = RoundedCornerShape(12.dp),

    colors = CardDefaults.cardColors(
      containerColor = Color(0xFF182235)
    )
  ) {

    Row(
      modifier = Modifier
        .fillMaxWidth()
        .padding(16.dp),

      horizontalArrangement = Arrangement.SpaceBetween
    ) {

      Column {

        Text(
          text = name,
          color = Color.White,
          fontWeight = FontWeight.Bold
        )

        Text(
          text = type,
          color = Color.Gray,
          fontSize = 12.sp
        )
      }

      Text(
        text = status,
        color = Color(0xFF22C55E),
        fontWeight = FontWeight.Bold
      )
    }
  }
}