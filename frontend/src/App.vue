<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from './api/client'

type Dashboard = { watch_folders: number; statuses: Record<string, number> }
type FileItem = { id: number; filename: string; relative_path: string; extension: string; size: number; status: string }
type WatchFolder = { id: number; name: string; root_path: string; inbox_path: string; dry_run: boolean; auto_processing: boolean }

const tab = ref('dashboard')
const dashboard = ref<Dashboard | null>(null)
const files = ref<FileItem[]>([])
const watchFolders = ref<WatchFolder[]>([])
const ollamaOk = ref<boolean | null>(null)
const error = ref('')
const notice = ref('')
const savingWatchFolder = ref(false)

const watchFolderForm = reactive({
  name: '未整理フォルダ',
  root_path: '/data/share',
  inbox_path: '/data/share/未整理',
  enabled: true,
  dry_run: true,
  auto_processing: false,
  auto_confidence_threshold: 0.95,
  max_file_size_mb: 100,
  allowed_extensions: ['.txt', '.md', '.csv', '.json', '.pdf', '.docx', '.xlsx'],
  exclude_patterns: ['~$*', '*.tmp', '*.part', '*.crdownload', '.DS_Store', 'Thumbs.db'],
  scan_interval_seconds: 300,
  realtime_watch: false,
})

async function refresh() {
  error.value = ''
  try {
    const [dashboardResponse, filesResponse, watchFoldersResponse] = await Promise.all([
      api.get('/dashboard'),
      api.get('/files'),
      api.get('/watch-folders'),
    ])
    dashboard.value = dashboardResponse.data
    files.value = filesResponse.data
    watchFolders.value = watchFoldersResponse.data
  } catch {
    error.value = 'APIからデータを取得できませんでした。'
  }
}

async function checkOllama() {
  try {
    const response = await api.get('/ollama/status')
    ollamaOk.value = Boolean(response.data.ok)
  } catch {
    ollamaOk.value = false
  }
}

async function createWatchFolder() {
  savingWatchFolder.value = true
  error.value = ''
  notice.value = ''
  try {
    await api.post('/watch-folders', watchFolderForm)
    notice.value = '監視フォルダ設定を登録しました。Dry Runは有効のままです。'
    await refresh()
  } catch {
    error.value = '監視フォルダ設定を登録できませんでした。パスとAPIログを確認してください。'
  } finally {
    savingWatchFolder.value = false
  }
}

onMounted(() => {
  refresh()
  checkOllama()
})
</script>

<template>
  <v-app>
    <v-navigation-drawer>
      <v-list-item title="Ollama File Organizer" subtitle="安全重視のAI整理" prepend-icon="mdi-robot-outline" />
      <v-divider />
      <v-list nav>
        <v-list-item title="ダッシュボード" prepend-icon="mdi-view-dashboard-outline" @click="tab = 'dashboard'" />
        <v-list-item title="ファイル" prepend-icon="mdi-file-tree-outline" @click="tab = 'files'" />
        <v-list-item title="設定" prepend-icon="mdi-cog-outline" @click="tab = 'settings'" />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar title="Ollama File Organizer">
      <template #append><v-chip color="warning" variant="tonal">Dry Run推奨</v-chip></template>
    </v-app-bar>

    <v-main>
      <v-container fluid class="pa-6">
        <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
        <v-alert v-if="notice" type="success" class="mb-4">{{ notice }}</v-alert>

        <template v-if="tab === 'dashboard'">
          <div class="d-flex align-center mb-6">
            <h1 class="text-h4">ダッシュボード</h1><v-spacer /><v-btn prepend-icon="mdi-refresh" @click="refresh">更新</v-btn>
          </div>
          <v-row>
            <v-col cols="12" md="4"><v-card title="監視フォルダ" :text="String(dashboard?.watch_folders ?? 0)" /></v-col>
            <v-col cols="12" md="4"><v-card title="未処理" :text="String(dashboard?.statuses?.discovered ?? 0)" /></v-col>
            <v-col cols="12" md="4"><v-card title="承認待ち" :text="String(dashboard?.statuses?.pending_approval ?? 0)" /></v-col>
          </v-row>
          <v-card class="mt-6" title="登録済み監視フォルダ">
            <v-list v-if="watchFolders.length">
              <v-list-item v-for="item in watchFolders" :key="item.id" :title="item.name" :subtitle="`${item.inbox_path} / Dry Run: ${item.dry_run ? 'ON' : 'OFF'}`" />
            </v-list>
            <v-card-text v-else>まだ登録されていません。</v-card-text>
          </v-card>
        </template>

        <template v-else-if="tab === 'files'">
          <h1 class="text-h4 mb-6">ファイル</h1>
          <v-card>
            <v-table>
              <thead><tr><th>ファイル名</th><th>相対パス</th><th>拡張子</th><th>サイズ</th><th>状態</th></tr></thead>
              <tbody>
                <tr v-for="item in files" :key="item.id">
                  <td>{{ item.filename }}</td><td>{{ item.relative_path }}</td><td>{{ item.extension }}</td><td>{{ item.size }}</td><td>{{ item.status }}</td>
                </tr>
              </tbody>
            </v-table>
          </v-card>
        </template>

        <template v-else>
          <h1 class="text-h4 mb-6">設定</h1>
          <v-alert type="warning" variant="tonal" class="mb-6">初回運用はDry Runを有効にし、自動整理を無効のまま確認してください。</v-alert>

          <v-row>
            <v-col cols="12" lg="5">
              <v-card title="Ollama接続">
                <v-card-text>
                  <v-chip :color="ollamaOk ? 'success' : 'error'" variant="tonal">{{ ollamaOk ? '接続済み' : '未接続' }}</v-chip>
                  <v-btn class="ml-4" @click="checkOllama">再確認</v-btn>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" lg="7">
              <v-card title="監視フォルダ登録">
                <v-card-text>
                  <v-text-field v-model="watchFolderForm.name" label="表示名" />
                  <v-text-field v-model="watchFolderForm.root_path" label="許可ルートパス" hint="例: /data/share" persistent-hint />
                  <v-text-field v-model="watchFolderForm.inbox_path" label="未整理フォルダ" hint="許可ルート配下を指定" persistent-hint />
                  <div class="d-flex ga-6 mt-4">
                    <v-switch v-model="watchFolderForm.dry_run" color="warning" label="Dry Run" />
                    <v-switch v-model="watchFolderForm.auto_processing" color="error" label="自動整理" :disabled="watchFolderForm.dry_run" />
                  </div>
                  <v-btn color="primary" :loading="savingWatchFolder" @click="createWatchFolder">登録</v-btn>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </v-container>
    </v-main>
  </v-app>
</template>
