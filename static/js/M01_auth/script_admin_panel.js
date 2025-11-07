/**
 * SIGMA-PLI - Script do Painel Administrativo
 * Gerencia funcionalidades da página /admin/panel
 */

document.addEventListener('DOMContentLoaded', function() {
  // Carregar métricas iniciais
  loadMetrics();
  
  // Carregar atividades recentes
  loadRecentActivities();
  
  // Atualizar uptime do sistema
  updateSystemUptime();
  
  // Event listeners para botões de ação
  setupActionButtons();
  
  // Atualização automática a cada 30 segundos
  setInterval(loadMetrics, 30000);
  setInterval(loadRecentActivities, 60000);
  setInterval(updateSystemUptime, 1000);
});

/**
 * Carrega métricas do dashboard administrativo
 */
async function loadMetrics() {
  try {
    // Simular chamada à API (substituir por endpoint real)
    const response = await fetch('/api/v1/admin/metrics', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      updateMetricsUI(data);
    } else {
      // Usar dados simulados se a API não estiver disponível
      updateMetricsUI({
        total_users: 42,
        active_users: 38,
        pending_requests: 5,
        active_sessions: 12
      });
    }
  } catch (error) {
    console.error('Erro ao carregar métricas:', error);
    // Dados simulados como fallback
    updateMetricsUI({
      total_users: 42,
      active_users: 38,
      pending_requests: 5,
      active_sessions: 12
    });
  }
}

/**
 * Atualiza interface com métricas
 */
function updateMetricsUI(data) {
  document.getElementById('totalUsers').textContent = data.total_users || '-';
  document.getElementById('activeUsers').textContent = data.active_users || '-';
  document.getElementById('pendingRequests').textContent = data.pending_requests || '-';
  document.getElementById('activeSessions').textContent = data.active_sessions || '-';
}

/**
 * Carrega atividades recentes
 */
async function loadRecentActivities() {
  try {
    const response = await fetch('/api/v1/admin/recent-activities?limit=10', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      updateActivitiesTable(data.activities || []);
    } else {
      // Dados simulados
      updateActivitiesTable([
        {
          timestamp: new Date().toISOString(),
          user: 'admin@sigma.gov.br',
          action: 'Login realizado',
          status: 'success'
        },
        {
          timestamp: new Date(Date.now() - 300000).toISOString(),
          user: 'usuario@empresa.com.br',
          action: 'Cadastro de Pessoa Física',
          status: 'success'
        },
        {
          timestamp: new Date(Date.now() - 600000).toISOString(),
          user: 'gestor@orgao.gov.br',
          action: 'Aprovação de solicitação',
          status: 'success'
        }
      ]);
    }
  } catch (error) {
    console.error('Erro ao carregar atividades:', error);
    updateActivitiesTable([]);
  }
}

/**
 * Atualiza tabela de atividades
 */
function updateActivitiesTable(activities) {
  const tbody = document.querySelector('#recentActivities tbody');
  
  if (activities.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" class="text-center text-muted">
          Nenhuma atividade recente encontrada
        </td>
      </tr>
    `;
    return;
  }
  
  tbody.innerHTML = activities.map(activity => {
    const date = new Date(activity.timestamp);
    const statusBadge = getStatusBadge(activity.status);
    
    return `
      <tr>
        <td>${formatDateTime(date)}</td>
        <td>${activity.user}</td>
        <td>${activity.action}</td>
        <td>${statusBadge}</td>
      </tr>
    `;
  }).join('');
}

/**
 * Retorna badge HTML para status
 */
function getStatusBadge(status) {
  const badges = {
    'success': '<span class="badge bg-success">Sucesso</span>',
    'pending': '<span class="badge bg-warning">Pendente</span>',
    'failed': '<span class="badge bg-danger">Falhou</span>',
    'cancelled': '<span class="badge bg-secondary">Cancelado</span>'
  };
  
  return badges[status] || '<span class="badge bg-info">Desconhecido</span>';
}

/**
 * Formata data/hora
 */
function formatDateTime(date) {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  
  return `${day}/${month}/${year} ${hours}:${minutes}`;
}

/**
 * Atualiza uptime do sistema
 */
let startTime = Date.now();

function updateSystemUptime() {
  const uptime = Math.floor((Date.now() - startTime) / 1000);
  const hours = Math.floor(uptime / 3600);
  const minutes = Math.floor((uptime % 3600) / 60);
  const seconds = uptime % 60;
  
  document.getElementById('systemUptime').textContent = 
    `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

/**
 * Configura event listeners para botões de ação
 */
function setupActionButtons() {
  // Logs do Sistema
  document.getElementById('btnViewLogs')?.addEventListener('click', function() {
    showAlert('info', 'Funcionalidade em desenvolvimento', 'A visualização de logs será implementada em breve.');
  });
  
  // Configurações
  document.getElementById('btnSettings')?.addEventListener('click', function() {
    showAlert('info', 'Funcionalidade em desenvolvimento', 'O painel de configurações será implementado em breve.');
  });
  
  // Backup e Restauração
  document.getElementById('btnBackup')?.addEventListener('click', function() {
    showAlert('info', 'Funcionalidade em desenvolvimento', 'O gerenciamento de backups será implementado em breve.');
  });
}

/**
 * Exibe alerta na área de alertas
 */
function showAlert(type, title, message) {
  const alertsContainer = document.getElementById('adminAlerts');
  const alertClass = {
    'success': 'alert-success',
    'info': 'alert-info',
    'warning': 'alert-warning',
    'danger': 'alert-danger'
  }[type] || 'alert-info';
  
  const alertHTML = `
    <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
      <strong>${title}</strong>
      <p class="small mb-0">${message}</p>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
  
  alertsContainer.insertAdjacentHTML('beforeend', alertHTML);
  
  // Auto-remover após 5 segundos
  setTimeout(() => {
    const alerts = alertsContainer.querySelectorAll('.alert');
    if (alerts.length > 3) {
      alerts[0].remove();
    }
  }, 5000);
}
